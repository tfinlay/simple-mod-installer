import logging
import os
from flask import Blueprint, request, flash, render_template, redirect, abort, jsonify
from werkzeug.utils import secure_filename
from simple_mod_installer import mod as m, config
from simple_mod_installer.util import join_path, resolve_url_bool
from simple_mod_installer.util.http import download_to_file
from simple_mod_installer import exceptions, searchmods
from urllib.error import URLError, HTTPError
from urllib.parse import urlsplit

mod = Blueprint(
    'mod',
    __name__,
    template_folder='../../templates'
)
logger = logging.getLogger(__name__)

UPLOADS_DIR = join_path(
                config["application_root"],
                "tmp",
                "uploads"
)

'''
@mod.route('/')
def index():
    return render_template('mod_index.html', mods=m.all())


@mod.route('/<id>')
def view_mod(id):
    """
    Displays a Mod
    :param id: int, is of the mod
    """
    try:
        return render_template('mod_view.html', mod=m.get_from_id(id))
    except exceptions.ModNotExistError:  # a collection with this id doesn't exist
        abort(404)
'''


@mod.route('/add/upload', methods=['POST'])
def upload_mod():
    """
    Ability to upload a mod file to be added to the mod pool
    :return:
    """
    if request.method == 'POST':
        logger.info("Got mod upload request with files: {}".format(request.files))

        # check there's a file:
        if 'file' not in request.files:
            logger.error("No file part found")
            return jsonify(dict(
                status="error",
                title="No mod to upload",
                body="Please select a mod file to upload.",
                code="InvalidFile"
            ))

        file = request.files['file']

        logger.info("Got file: {} with filename: `{}`".format(file, file.filename))

        if file.filename == '':
            logger.error("file.filename is empty")
            return jsonify(dict(
                status="error",
                title="No mod to upload",
                body="Please select a mod file to upload.",
                code="InvalidFile"
            ))
        if file and m.allowed_modfile(file.filename):
            filename = secure_filename(file.filename)
            temp_path = join_path(
                UPLOADS_DIR,
                filename
            )

            if not os.path.exists(UPLOADS_DIR):
                os.makedirs(UPLOADS_DIR)

            file.save(temp_path)

            try:
                modid = m.add(
                    temp_path,
                    ignore_modexist_error=resolve_url_bool(request.args.get("overwrite"))
                )
            except exceptions.ModExistsError:
                return jsonify(dict(
                    status="error",
                    title="No mods found",
                    body="Please select a valid mod file to upload.",
                    code="ModExistsError"
                    # try again with arg ignore_modexist_error=True
                ))
            else:
                return jsonify(dict(
                    status="success",
                    modid=modid
                ))


@mod.route('/add/curse', methods=['POST'])
def curse_mod():
    """
    Download a mod from Curse, populating it's metadata in the database
    :return:
    """
    if request.method == 'POST':
        if not request.args.get("curse_id"):
            abort(400)

        if not request.args.get("file_id"):
            abort(400)

        if not request.args.get("url"):
            abort(400)

        # get download url
        url = request.args.get("url")
        try:
            # download the mod
            temp_path = join_path(
                config["application_root"],
                "tmp",
                "uploads",
                urlsplit(
                    url
                ).path.split('/')[-1]
            )

            download_to_file(
                url,
                temp_path
            )

            try:
                return jsonify(dict(
                    status='success',
                    modid=m.add(
                        temp_path,
                        url,
                        curse_id=request.args.get("curse_id"),
                        curse_file_id=request.args.get("file_id"),
                        ignore_modexist_error=resolve_url_bool(request.args.get("overwrite"))
                    )
                ))
            except exceptions.ModExistsError:
                return jsonify(dict(
                    status='error',
                    title="Mod already exists",
                    body="Please select a valid mod file to download.",
                    code="ModExistsError"
                ))

        except HTTPError as e:
            logger.error("Failed to download Modfile: {} ({} - {})".format(
                e.filename,
                type(e),
                e
            ))
            abort(e.code)
        except URLError as e:
            logger.error("Failed to download ModFile: {}".format(
                e.filename
            ))
            abort(400)
        except Exception:
            raise


@mod.route('/add/download', methods=['POST'])
def download_mod():
    """
    Ability to download a mod file to be added to the mod pool, from a direct download link
    :return:
    """
    if request.method == 'POST':
        if not request.args.get("url"):
            abort(400)
        else:
            try:
                temp_path = join_path(
                    config["application_root"],
                    "tmp",
                    "uploads",
                    urlsplit(
                        request.args.get("url")
                    ).path.split('/')[-1]
                )

                download_to_file(
                    request.args.get("url"),
                    temp_path
                )
                try:
                    return redirect("/mod/{}".format(m.add(
                        temp_path,
                        request.args.get("url"),
                        ignore_modexist_error=resolve_url_bool(request.args.get("overwrite"))
                    )))
                except exceptions.ModExistsError:
                    return render_template('confirm.html', title="Confirmation required", desc="")

            except HTTPError as e:
                logger.error("Failed to download Modfile: {}".format(
                    e.filename
                ))
                abort(e.code)
            except URLError as e:
                logger.error("Failed to download ModFile: {}".format(
                    e.filename
                ))
                abort(400)
            except Exception:
                raise


@mod.route('/remove', methods=['POST'])
def remove_mod():
    """
    Removes a mod
    :return:
    """
    logger.debug("Received request to remove Mod with id: {}".format(request.args.get("id")))
    id = request.args.get("id")
    if request.method == 'POST':
        if not id:
            logger.error("ID URL parameter is invalid")
            abort(400)

        try:
            m.remove(int(id))
            return jsonify(dict(
                status="success"
            ))
        except exceptions.ModNotExistError as ex:
            logger.error("Mod with id {} cannot be deleted, because it doesn't exist".format(id))
            abort(400)
        except exceptions.ModInfoNotExistError as ex:
            logger.critical("Mod doesn't have critical data associated with it. Something is wrong!")
            abort(500)


@mod.route('/<int:id>.json')
def mod_json(id):
    """
    Returns JSON data about the mod
    :param id: int
    """
    try:
        x = m.get_from_id(id)
    except exceptions.ModNotExistError:
        abort(404)
    else:
        return jsonify(dict(
            name=x.name,
            modid=x.modid,
            version=x.version,
            mc_version=x.mc_version,
            update_json_url=x.update_json_url,
            description=x.description,
            credits=x.credits
        ))


# Search


@mod.route('/search')
def search_for_mods():
    """
    Search the database, and external sources if available, for mods matching the search term, and perhaps the collection if specified.
    """
    logger.info("Got mod search request")
    response = searchmods.raw_search(
        request.args.get("term"),
        request.args.get("context"),
        True if request.args.get("local") == 'true' else False,
        True if request.args.get("remote") == 'true' else False
    )

    return jsonify([x.jsonify() for x in response])

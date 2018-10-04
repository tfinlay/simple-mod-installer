"""
Collection-related pages
"""
import logging
from flask import Blueprint, render_template, abort, request, redirect, flash, jsonify, url_for
from simple_mod_installer import collection as coll, config
from simple_mod_installer.collection.checks import dependency_check
from simple_mod_installer import exceptions
from simple_mod_installer import util
from simple_mod_installer import mc_interface

collection = Blueprint(
    'collection',
    __name__,
    template_folder="../../templates"
)

logger = logging.getLogger(__name__)

'''
@collection.route('/')
def index():
    """
    Index, shows a list of all collections
    :return:
    """
    return render_template('collection_index.html', collections=coll.all())


@collection.route('/<id>')
def view_collection(id):
    """
    Displays a collection
    :param id: int, is of the collection
    :return:
    """
    logger.info("Collection View requested for collection with id: {}".format(id))
    try:
        return render_template('collection_view.html', collection=coll.get_from_id(id))
    except exceptions.CollectionNotExistError:  # a collection with this id doesn't exist
        logger.error("Collection with id: {} does not exist".format(id))
        abort(404)
'''


@collection.route('/add', methods=['POST'])
def create_collection():
    if request.method == 'POST':
        if not util.verify_name(request.args.get("name")):
            logger.error("Invalid Name")
            flash("Please specify a name")
            abort(400)
        if not util.verify_name(request.args.get("mcversion")):
            logger.error("Invalid McVersion")
            flash("Please specify an mcversion")
            abort(400)
        if not request.args.get("version-id") in mc_interface.get_version_names():
            logger.error("Invalid version id: {}".format(request.args.get("version-id")))
            flash("Please enter a valid version id")
            abort(400)

        try:
            x = coll.add(
                    request.args.get("name"),
                    request.args.get("mcversion"),
                    request.args.get("version-id")
                )

            return jsonify(dict(
                status="success",
                collid=x
            ))

        except exceptions.CollectionExistsError as ex:
            return jsonify(dict(
                status="error",
                title="Collection already exists",
                body="A collection by this name already exists",
                code="CollectionExistsError",
                collid=ex.id
            ))
        except Exception:
            raise


@collection.route('/remove', methods=['POST'])
def remove_collection():
    if request.method == 'POST':
        if str(request.args.get("id")).isdigit():
            try:
                name = coll.remove(int(request.args.get("id")))
                return "<h1>Deletion of Collection: '{}' sucessful!</h1>".format(name)
            except exceptions.CollectionNotExistError:
                abort(400)
            except Exception:
                raise


@collection.route('/<int:id>/add_mod', methods=['POST'])
def add_mod(id):
    """
    adds a mod
    :param id: int, id of the collection to add the mod to
    :return:
    """
    if request.method == 'POST':
        logger.info("Adding mod...")
        if request.args.get("id") is not None:
            logger.debug("ID url parameter is specified.")
            try:
                coll.add_mod(id, request.args.get("id"))
            except exceptions.CollectionNotExistError as ex:
                logger.error("Collection with id: {} doesn't exist".format(ex.id))
                abort(400)
            except exceptions.ModNotExistError as ex:
                logger.error("Mod with id: {} doesn't exist".format(ex.id))
                abort(400)
            except OSError:
                logger.error("An OSError occurred, passing that up to the client...")
                return jsonify(dict(
                    status="error",
                    title="Link error",
                    body="We don't have permission to link this mod, please restart the program with administrator permissions.",
                    code="SymLinkError"
                ))

            logger.info("Mod added the collection successfully")
            return jsonify(dict(
                status="success"
            ))
        else:
            logger.error("ID url parameter was not specified")
            abort(400)


@collection.route('/<int:id>/rem_mod', methods=['POST'])
def rem_mod(id):
    """
    Removes a mod
    :param id: int, id of the collection to remove the mod from
    :return:
    """
    if request.method == 'POST':
        logger.info("Removing mod from collection: {}".format(id))
        if request.args.get("id") is not None:
            logger.debug("ID url parameter is specified")
            try:
                coll.rem_mod(id, request.args.get("id"))
            except exceptions.CollectionNotExistError as ex:
                logger.error("Collection with id: {} doesn't exist".format(ex.id))
                abort(400)
            except exceptions.ModNotExistError as ex:
                logger.error("Mod with id: {} doesn't exist".format(ex.id))
                abort(400)
            logger.info("Mod removed from collection successfully")
            return jsonify(dict(
                status="success"
            ))
        else:
            logger.error("ID url parameter was not specified")
            abort(400)


@collection.route('/<int:id>/dep_check', methods=['POST'])
def dep_check_mod(id):
    """
    TESTING: dependency check a mod
    :param id: int
    :return:
    """
    logger.info("Checking dependencies for collection: {}".format(id))
    c = coll.get_from_id(id)
    print(c.mods)
    return "<p>{}</p>".format(dependency_check(c))


def getcoll(id):
    try:
        return coll.get_from_id(id)
    except exceptions.CollectionNotExistError:
        abort(404)


@collection.route('.json')
def coll_list_data():
    """
    A list of all of the collections we have, ordered by creation date
    """
    # get the raw data
    collections = coll.Collection.query.order_by(coll.Collection.epoch_created.desc()).all()

    return jsonify([
        dict(
            id=c.id,
            name=c.name,
            mc_version=c.mc_version,
        ) for c in collections
    ])


@collection.route('/<int:id>/browse', methods=["POST"])
def open_file_browser(id):
    c = getcoll(id)
    util.open_file_browser(
        util.join_path(
            config["application_root"],
            "collections",
            c.mc_id.decode()
        )
    )

    return jsonify(dict(
        status="success"
    ))


@collection.route('/<int:id>.json')
def coll_general_data(id):
    c = getcoll(id)
    return jsonify(dict(
        name=c.name,
        mc_version=c.mc_version,
        version_id=c.version_id,
        epoch_created=c.epoch_created
    ))


@collection.route('/<int:id>/mods.json')
def coll_mod_ids(id):
    c = getcoll(id)
    return jsonify([dict(
        id=m.id,
        name=m.name,
        modid=m.modid,
        version=m.version,
        filename=util.get_file_name(m.filename)
    ) for m in c.mods])


@collection.route('/<int:id>/issues/mcversion')
def coll_mcversion_check(id):
    c = getcoll(id)

    return jsonify(coll.checks.mcversion_check(c))


@collection.route('/<int:id>/issues/depcheck')
def coll_dependency_check(id):
    c = getcoll(id)

    if request.args.get("by_dependency"):
        return jsonify(coll.checks.dependency_check(c, group_by_dependency=True))
    else:
        return jsonify(coll.checks.dependency_check(c))

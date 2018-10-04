from simple_mod_installer.webserver import app
from flask import render_template, abort, redirect, jsonify, request, flash
from simple_mod_installer.database.models import *
from simple_mod_installer.database import db_session
from simple_mod_installer import collection, exceptions


@app.route('/')
def hello_world():
    return render_template("index.html")


def add_collection(args):
    """
    Add a collection to the database
    :param args:
    :return: None
    """
    lookup = Collection.query.filter(Collection.name == args.get("name")).first()
    print(lookup)
    if lookup:
        #return '/collection/{}'.format(lookup.id)  # a collection by that name already exists
        return "/collection/{}".format(lookup.id)
    else:
        coll = Collection(
            args.get("name"),
            args.get("mcversion"),
            args.get("version_id")
        )
        db_session.add(coll)
        db_session.commit()

        return '/collection/{}'.format(coll.id)
        #return redirect("/collection/{}".format(coll.id))


@app.route('/collection/<collectionid>', methods=['GET'])
def view_collection(collectionid):
    coll = Collection.query.get(collectionid)
    if coll is not None:
        return render_template('collection_view.html', collection=coll)
    else:
        print("Collection doesn't exist!")
        abort(404)


@app.route('/collection/add', methods=['POST'])
def create_collection():
    if request.method == 'POST':
        try:
            collection.add(
                request.args.get("name"),
                request.args.get("mcversion"),
                request.args.get("version-id")
            )
        except exceptions.CollectionExistsError as ex:
            return redirect('/collection/{}'.format(ex.id))

        # return redirect(add_collection(request.args))  # redirect to /collection/<collection_id>


@app.route('/mod/<modid>', methods=['GET'])
def request_mod_info(modid):
    return jsonify({}), 200, {'ContentType': 'application/json'}


def add_mod(file):
    """
    Adds a mod file to the database
    :param file:
    :return: None
    """



@app.route('/mod/add', methods=['GET', 'POST'])
def addmod_page():
    if request.method == 'GET':
        # serve the page
        ""
    elif request.method == 'POST':
        # receive the new data
        if 'file' not in request.files:
            flash("No file part")
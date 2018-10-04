"""
JavaScript API head
"""
import logging
from flask import Blueprint, jsonify, request, abort
from simple_mod_installer.mc_interface import forge

api = Blueprint(
    'api',
    __name__,
    template_folder="../../templates"
)

logger = logging.getLogger(__name__)


@api.route('/mcversions')
def get_mc_versions():
    """
    Returns an array of all of the valid, installed mcversions, and metadata associated with them
    :return:
    """
    return jsonify(forge.get_available_minecraft_releases())
    #return jsonify([version.dictify() for version in mc_interface.get_versions()])


@api.route('/search')
def search_mods():
    if not request.args.get("term"):
        abort(400)

    if request.args.get("collectionContext"):
        pass
        #context =
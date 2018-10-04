from urllib.request import unquote
from flask import Blueprint, render_template, request, send_from_directory, jsonify
from platform import system
import os.path

misc = Blueprint(
    'misc',
    __name__,
    template_folder='../../templates'
)


BASE_URL = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "static", "dist")

'''
@misc.route('/app/<path:filename>')
def client_app_app_folder(filename):
    return send_from_directory(
        os.path.join(CLIENT_APP_FOLDER, "app"),
        filename
    )
'''


@misc.route('/<path:filename>.<extension>')
def client_app_folder(filename, extension):
    #print(CLIENT_APP_FOLDER + '\\' + filename)

    return send_from_directory(
        CLIENT_APP_FOLDER,
        filename + "." + extension
    )


@misc.route('/')
def index():
    return render_template('main.html')


@misc.route('/confirm')
def confirm():
    title = request.args['title']
    desc = request.args['desc']
    action_url = unquote(request.args['action_url'])

    return render_template('_confirm.html', title=title, desc=desc, action_url=action_url)


@misc.route('/<path:path>')
def page_render(path):
    return render_template('main.html')


@misc.route('/restart_with_root')
def restart_with_root():
    """
    Restarts the application with root priviledges
    """
    return dict(jsonify(
        status='success'
    ))

import logging
from flask import Flask, request
from simple_mod_installer.database import db_session
from simple_mod_installer.util import join_path
from simple_mod_installer import config
from simple_mod_installer.webserver.pages import collection, mod, misc, api

logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_url_path='/',  # serve static from /css/main.css
    static_folder='static/dist',  # our static content folder is called static/dist
    template_folder='templates',
)

app.register_blueprint(collection.collection, url_prefix="/collection")
app.register_blueprint(mod.mod, url_prefix="/mod")
app.register_blueprint(api.api, url_prefix="/api")
app.register_blueprint(misc.misc)
app.secret_key = "super_secret_key"


#  close down the database at the end of the day
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

    #logger.info("Session ended with exception: {}. Database closed successfully.".format(exception))


def stop_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def start_server(debug=False):
    logger = logging.getLogger(__name__)
    logger.info("Starting Web Server...")

    import simple_mod_installer.webserver.pages  # link the pages up
    app.run(debug=debug, port=config["webserver_port"])
    logger.info("Web Server Running")


if __name__ == '__main__':
    logger.warning("Running server script instead of main script")
    start_server(debug=True)

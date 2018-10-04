# manage.py

from flask.ext.script import Manager

from simple_mod_installer import app

manager = Manager(app)


def crazy_call():
    print("crazy_call")


@manager.command
def runserver():
    app.run()
    import webbrowser
    webbrowser.open_new(app.static_url_path)


if __name__ == "__main__":
    manager.run()
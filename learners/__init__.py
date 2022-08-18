import os

from flask import Flask

from learners.logger import logger


def main():
    if os.getenv("REMOVE_DB"):
        logger.warn(" ******** REMOVE_DB is set. Deleting DB file ******** ")
        try:
            os.remove(os.path.join(os.getcwd(), "learners", "learners_tracker.db"))
        except:
            pass
    app = Flask(__name__)

    with app.app_context():

        from learners.conf.config import build_config

        build_config(app)

        from learners.database import build_db

        build_db(app)

        from learners.jwt_manager import init_jwt

        init_jwt(app)

        from learners.mail_manager import init_mail

        init_mail(app)

        from learners.socketio import init_socketio

        init_socketio(app)

    import learners.routes as routes

    app.register_blueprint(routes.home_api)
    app.register_blueprint(routes.authentication_api)
    app.register_blueprint(routes.interface_api)
    app.register_blueprint(routes.execution_api)
    app.register_blueprint(routes.callback_api)
    app.register_blueprint(routes.statics_api)
    app.register_blueprint(routes.admin_api)
    app.register_blueprint(routes.screensharing_api)

    return app


app = main()

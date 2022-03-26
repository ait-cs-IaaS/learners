from flask import Flask

import os
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

    from learners.routes.home import home_api
    from learners.routes.authentication import authentication_api
    from learners.routes.interface import interface_api
    from learners.routes.execution import execution_api
    from learners.routes.callback import callback_api
    from learners.routes.statics import statics_api
    from learners.routes.admin import admin_api

    app.register_blueprint(home_api)
    app.register_blueprint(authentication_api)
    app.register_blueprint(interface_api)
    app.register_blueprint(execution_api)
    app.register_blueprint(callback_api)
    app.register_blueprint(statics_api)
    app.register_blueprint(admin_api)

    return app


app = main()

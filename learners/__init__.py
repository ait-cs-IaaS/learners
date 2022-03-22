from flask import Flask
from flask_cors import CORS

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

        CORS(app)

    from learners import views

    app.register_blueprint(views.bp)

    return app


app = main()

from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt

import os
import logging


def main():

    if os.getenv("DEBUG"):
        logging.warn("  ******** Running in DEBUG Mode. ******************* ")
        logging.warn("  ******** Deleting DB file for testing. ************ ")
        logging.warn("  ******** (Set 'DEBUG'='false' to keep it.) ******** ")
        try:
            os.remove(os.path.join(os.getcwd(), "learners", "learners_tracker.db"))
        except:
            pass

    app = Flask(__name__)

    with app.app_context():

        """
        Set global configuration

        The configuration is set via the YAML file 'learners_config.yml' of the current working directory.
        To use a different config file, the path can be set via the environmant variable 'LEARNERS_CONFIG'.
        An example configuration can be found in 'learners_config.yml' in the root directory.
        """

        from learners.conf.config import build_config

        build_config(app)

        """
        Set up the database

        Learners keeps track of the training/exercise progress of the participants, for this
        a locale database is created, which is initialized with the following function.
        """

        from learners.database import build_db

        build_db(app)

        """
        Initialize JWT manager

        Learners uses JWT tokens for authentication, the necessary JWT manager is initialized
        in the following function.
        """

        from learners.jwt_manager import init_jwt

        init_jwt(app)

        """
        Initialize Mail manager

        In order to enable the option to send Emails, the mail manager is initialized in the
        following function.
        """

        from learners.mail_manager import init_mail

        init_mail(app)

        CORS(app)
        Bcrypt(app)

    from learners import views

    app.register_blueprint(views.bp)

    return app

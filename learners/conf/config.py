import contextlib
import json
import os
from datetime import timedelta

from flask_assets import Environment
from learners.logger import logger
from learners.assets import get_bundle
from strictyaml import YAMLError, load

cfg = None


class Configuration:
    def __init__(self):
        config_file = os.getenv("LEARNERS_CONFIG") or os.path.join(os.getcwd(), "config.yml")

        learners_config = {}
        from learners.conf.config_schema import config_schema

        try:
            with open(config_file, "r") as stream:
                yaml_config = stream.read()
                learners_config = load(yaml_config, config_schema).data
        except YAMLError as yamlerr:
            logger.exception(yamlerr)
            raise
        except EnvironmentError as enverr:
            logger.exception(enverr)
            raise
        self.jwt_secret_key = learners_config.get("jwt").get("jwt_secret_key")
        self.jwt_access_token_expires = timedelta(minutes=learners_config.get("jwt").get("jwt_access_token_duration"))

        self.jwt_for_vnc_access = learners_config.get("jwt").get("jwt_for_vnc_access")
        self.db_uri = learners_config.get("database").get("db_uri")
        self.novnc = {"server": learners_config.get("novnc").get("server")}
        self.users = json.loads(json.dumps(learners_config.get("users")).replace("DEFAULT-VNC-SERVER", self.novnc.get("server")))

        self.venjix = {
            "auth_secret": learners_config.get("venjix").get("auth_secret"),
            "url": learners_config.get("venjix").get("url"),
            "headers": {"Content-type": "application/json", "Authorization": f"Bearer {learners_config.get('venjix').get('auth_secret')}"},
        }

        self.callback = {"endpoint": learners_config.get("callback").get("endpoint")}
        self.theme = learners_config.get("learners").get("theme")
        self.landingpage = learners_config.get("learners").get("landingpage")
        self.language_code = learners_config.get("learners").get("language_code")
        self.static_base_url = learners_config.get("statics").get("directory")
        self.serve_mode = learners_config.get("statics").get("serve_mode")
        self.serve_documentation = learners_config.get("serve_documentation")
        self.serve_presentations = learners_config.get("serve_presentations")
        self.serve_exercises = learners_config.get("serve_exercises")
        self.exercise_json = learners_config.get("exercise_json")
        self.questionaire_json = learners_config.get("questionaire_json")
        self.questionaires_questions_json = learners_config.get("questionaires_questions_json")
        self.staticsites = learners_config.get("staticsites") or []
        self.upload_folder = learners_config.get("learners").get("upload_folder")
        self.allowed_extensions = learners_config.get("learners").get("upload_extensions")

        self.template = {
            "theme": self.theme,
            "branding": self.theme not in ["dark", "light"],
            "landingpage": self.landingpage,
            "chat": False,
            "staticsites": self.staticsites,
        }


def build_config(app):

    global cfg
    cfg = Configuration()

    config_app(app)

    if os.getenv("REMOVE_DB"):
        logger.warning(" ****** REMOVE_DB is set. Deleting DB file ****** ")

        db_path = (cfg.db_uri).split("sqlite:///")[1]
        if not (db_path).startswith("/"):
            db_path = os.path.join(app.root_path, db_path)

        with contextlib.suppress(Exception):
            os.remove(db_path)


def config_app(app):

    Environment(app).register(get_bundle(cfg.theme))

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = cfg.jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = cfg.jwt_access_token_expires
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"

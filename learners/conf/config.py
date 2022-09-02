import json
import os
from datetime import timedelta

from flask_assets import Environment
from learners import logger
from learners.assets import get_bundle
from strictyaml import YAMLError, load

cfg = None


class Configuration:
    def __init__(self):

        config_file = os.getenv("LEARNERS_CONFIG") or os.path.join(os.getcwd(), "config.yml")

        learners_config = {}

        # import schema specifications
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

        # Set jwt related configuration
        self.jwt_secret_key = learners_config.get("jwt").get("jwt_secret_key")
        self.jwt_access_token_expires = timedelta(minutes=learners_config.get("jwt").get("jwt_access_token_duration"))
        self.jwt_for_vnc_access = learners_config.get("jwt").get("jwt_for_vnc_access")

        # Set database configuration
        self.db_uri = learners_config.get("database").get("db_uri")

        novnc = {"server": learners_config.get("novnc").get("server")}
        users = learners_config.get("users")
        self.users = json.loads(json.dumps(users).replace("DEFAULT-VNC-SERVER", novnc.get("server")))

        self.venjix = {
            "auth_secret": learners_config.get("venjix").get("auth_secret"),
            "url": learners_config.get("venjix").get("url"),
            "headers": {
                "Content-type": "application/json",
                "Authorization": f"Bearer {learners_config.get('venjix').get('auth_secret')}",
            },
        }

        self.callback = {"endpoint": learners_config.get("callback").get("endpoint")}

        # Set learners configuration
        self.theme = learners_config.get("learners").get("theme")
        self.language_code = learners_config.get("learners").get("language_code")

        # Set static content
        self.static_base_url = learners_config.get("statics").get("directory")
        self.serve_mode = learners_config.get("statics").get("serve_mode")

        self.serve_documentation = learners_config.get("serve_documentation")
        self.serve_presentations = learners_config.get("serve_presentations")
        self.serve_exercises = learners_config.get("serve_exercises")
        self.exercise_json = learners_config.get("exercise_json")

        # Define additional static sites
        staticsites = learners_config.get("staticsites") or []

        # Set Upload settings
        self.upload_folder = learners_config.get("learners").get("upload_folder")
        self.allowed_extensions = learners_config.get("learners").get("upload_extensions")

        # Create template config for rendering
        self.template = {
            "theme": self.theme,
            "branding": bool(self.theme != "dark" and self.theme != "light"),
            "chat": False,
            "staticsites": staticsites,
        }


def build_config(app):

    global cfg
    cfg = Configuration()

    config_app(app)


def config_app(app):

    Environment(app).register(get_bundle(cfg.theme))

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = cfg.jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = cfg.jwt_access_token_expires
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"

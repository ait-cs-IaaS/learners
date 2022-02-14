import os
from datetime import timedelta
from passlib.apache import HtpasswdFile

from flask_assets import Environment
from learners.assets import get_bundle

from strictyaml import load, YAMLError


cfg = None


class Configuration:

    """
    Holds global configuration

    This class is used to access application-wide predefined parameters and variables created at
    runtime. The attributes are initialized via the config YAML file (default: 'learners_config.yml'
    of current directory, but can be set via the environmant variable 'LEARNERS_CONFIG'). These must
    correspond to the schema in 'config_schema.py'.
    """

    def __init__(self):

        """
        Returns the value of the environmant variable 'LEARNERS_CONFIG' if it's not None, else the
        current working directory is concatenated with 'learners_config.yml'
        """
        config_file = os.getenv("LEARNERS_CONFIG") or os.path.join(os.getcwd(), "learners_config.yml")

        learners_config = {}

        # import schema specifications
        from learners.conf.config_schema import config_schema

        try:
            with open(config_file, "r") as stream:
                yaml_config = stream.read()
                learners_config = load(yaml_config, config_schema).data
        except YAMLError as yamlerr:
            print(yamlerr)
            raise
        except EnvironmentError as enverr:
            print(enverr)
            raise

        # Set learners configuration
        self.theme = learners_config.get("learners").get("theme")
        self.branding = learners_config.get("learners").get("branding")
        self.language = learners_config.get("learners").get("language")
        self.htpasswd = HtpasswdFile(learners_config.get("learners").get("htpasswd"))

        # Set jwt related configuration
        self.jwt_secret_key = learners_config.get("jwt", {}).get("jwt_secret_key", "53CR3T")
        self.jwt_access_token_expires = timedelta(minutes=learners_config.get("jwt").get("jwt_access_token_duration"))
        self.jwt_for_vnc_access = learners_config.get("jwt").get("jwt_for_vnc_access")

        # Set database configuration
        self.db_uri = learners_config.get("database").get("db_uri")

        # Set components configuration
        self.url_novnc = learners_config.get("components").get("urls").get("novnc")
        self.url_callback = learners_config.get("components").get("urls").get("callback")
        self.url_documentation = learners_config.get("components").get("urls").get("documentation")
        self.url_exercises = learners_config.get("components").get("urls").get("exercises")
        self.url_venjix = learners_config.get("components").get("urls").get("venjix")
        self.venjix_auth_secret = learners_config.get("components").get("venjix_auth_secret")

        # define the render template
        self.template = {
            "authenticated": False,
            "user_id": None,
            "branding": self.branding,
            "theme": self.theme,
            "vnc_clients": None,
            "docs_url": None,
            "exercises_url": None,
        }

        # Set user mappings
        self.user_assignments = learners_config.get("components").get("user_assignments")

        # set CORS configuration
        self.cors_origins = []
        for user in self.user_assignments:
            self.cors_origins.append(self.url_documentation + ":" + str(self.user_assignments.get(user).get("ports").get("docs")))
            self.cors_origins.append(self.url_exercises + ":" + str(self.user_assignments.get(user).get("ports").get("exercises")))


def build_config(app):

    """
    Set global configuration

    This function instantiates a global configuration class that can be imported from other files.
    """

    global cfg
    cfg = Configuration()

    # Set flask app.config
    config_app(app)


def config_app(app):

    """
    Set app.config

    This function sets the required app.configs (SQLALCHEMY, JWT, CORS) and enables the use of SCSS.
    """

    Environment(app).register(get_bundle(cfg.theme))

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = cfg.jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = cfg.jwt_access_token_expires
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]

    app.config["CORS_HEADERS"] = "Content-Type"
    app.config["CORS_ORIGINS"] = cfg.cors_origins
    app.config["CORS_SUPPORTS_CREDENTIALS"] = True

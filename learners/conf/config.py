import os
from datetime import timedelta

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

        # Set jwt related configuration
        self.jwt_secret_key = learners_config.get("jwt", {}).get("jwt_secret_key", "53CR3T")
        self.jwt_access_token_expires = timedelta(minutes=learners_config.get("jwt").get("jwt_access_token_duration"))
        self.jwt_for_vnc_access = learners_config.get("jwt").get("jwt_for_vnc_access")

        # Set database configuration
        self.db_uri = learners_config.get("database").get("db_uri")

        # Set mail configuration
        if learners_config.get("mail") is not None:
            self.mail = True
            self.mail_server = learners_config.get("mail").get("server")
            self.mail_port = learners_config.get("mail").get("port")
            self.mail_username = learners_config.get("mail").get("username")
            self.mail_password = learners_config.get("mail").get("password")
            self.mail_tls = learners_config.get("mail").get("tls")
            self.mail_ssl = learners_config.get("mail").get("ssl")
        elif os.getenv("MAIL"):
            self.mail = True
            self.mail_server = os.getenv("MAIL_SERVER") or ""
            self.mail_port = os.getenv("MAIL_PORT") or 587
            self.mail_username = os.getenv("MAIL_USERNAME") or ""
            self.mail_password = os.getenv("MAIL_PASSWORD") or ""
            self.mail_tls = os.getenv("MAIL_TLS") or True
            self.mail_ssl = os.getenv("MAIL_SSL") or False
        else:
            self.mail = False

        self.users = learners_config.get("users")

        # Set components configuration
        self.novnc = {
            "server": learners_config.get("novnc").get("server")
        }

        self.callback = {
            "endpoint": learners_config.get("callback").get("endpoint")
        }

        self.documentation = {
            "directory": learners_config.get("documentation").get("directory"),
            "endpoint": learners_config.get("documentation").get("endpoint")
        }

        self.exercises = {
            "directory": learners_config.get("exercises").get("directory"),
            "endpoint": learners_config.get("exercises").get("endpoint")
        }

        self.venjix = {
            "auth_secret": learners_config.get("venjix").get("auth_secret"),
            "url": learners_config.get("venjix").get("url")
        }

        # define the render template
        self.template = {
            "authenticated": False,
            "chat": False,
            "user_id": None,
            "branding": self.branding,
            "theme": self.theme,
            "vnc_clients": None,
            "url_documentation": None,
            "url_exercises": None,
        }

        # set CORS configuration
        self.cors_origins = []


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

    if cfg.mail:
        app.config["MAIL_SERVER"] = cfg.mail_server
        app.config["MAIL_PORT"] = cfg.mail_port
        app.config["MAIL_USERNAME"] = cfg.mail_username
        app.config["MAIL_PASSWORD"] = cfg.mail_password
        app.config["MAIL_USE_TLS"] = cfg.mail_tls
        app.config["MAIL_USE_SSL"] = cfg.mail_ssl

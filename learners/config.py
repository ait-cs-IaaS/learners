from flask_assets import Environment
import os
import yaml
from datetime import timedelta
from passlib.apache import HtpasswdFile
from learners.assets import get_bundle


cfg = None


class Configuration:
    def __init__(self, app):
        app.config.from_file(os.path.join(os.getcwd(), "learners_config.yml"), load=yaml.full_load)
        self.app_config = app.config
        self.app_config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=self.app_config["JWT_ACCESS_TOKEN_DURATION"])
        self.htpasswd = HtpasswdFile(self.app_config["LEARNERS_HTPASSWD"])

        self.assets = Environment(app)
        self.assets.register(get_bundle(self.app_config["THEME"]))

        self.template = dict(
            user_id="",
            branding=app.config["BRANDING"],
            theme=app.config["THEME"],
            vnc_clients=app.config["VNC_CLIENTS"],
            docs_url="",
            exercises_url="",
        )

    def get_app_config(self):
        return self.app_config

    def get_template(self):
        return self.template

    def get_assets(self):
        return self.assets

    def get_htpasswd(self):
        return self.htpasswd


def build_config(app):
    global cfg
    cfg = Configuration(app)

    return cfg.app_config

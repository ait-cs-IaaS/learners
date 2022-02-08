from flask_assets import Environment

import os
import yaml

from datetime import timedelta
from passlib.apache import HtpasswdFile
from learners.assets import get_bundle

template_config = {}
htpasswd = ""


def set_config(app):
    global template_config, htpasswd

    app.config.from_file(os.path.join(os.getcwd(), "learners_config.yml"), load=yaml.full_load)

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=app.config["JWT_ACCESS_TOKEN_DURATION"])
    htpasswd = HtpasswdFile(app.config["LEARNERS_HTPASSWD"])

    assets = Environment(app)
    theme_bundle = get_bundle(app.config["THEME"])
    assets.register(theme_bundle)

    template_config = dict(
        user_id="",
        branding=app.config["BRANDING"],
        theme=app.config["THEME"],
        vnc_clients=app.config["VNC_CLIENTS"],
        docs_url="",
        exercises_url="",
    )




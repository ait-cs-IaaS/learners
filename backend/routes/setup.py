from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, current_user, jwt_required
from backend.classes.Tab import Tab
from backend.conf.config import cfg
from backend.jwt_manager import admin_required

from backend.logger import logger

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/setup/login", methods=["GET"])
def getLoginInfo():

    # TODO: get from config file
    return jsonify(
        headline="Welcome to the",
        headlineHighlight="CyberRange",
        welcomeText="This is the entry point to the virtual environment of the simulation.<br>Please log in with your assigned credentials:",
        landingpage=cfg.landingpage,
        logo=cfg.logo,
    )


@setup_api.route("/setup/tabs", methods=["GET"])
@jwt_required(optional=True)
def getSidebar():

    landingpage = cfg.landingpage

    if not current_user:
        return jsonify(tabs=None, landingpage=landingpage, logo=cfg.logo)

    tabs = []

    if current_user.admin:
        tabs.append(Tab(id="admin", _type="admin").__dict__)
        landingpage = "admin"

    for tab_id, tab_details in cfg.tabs.get("standard").items():
        tabs.append(Tab(id=tab_id, _type="standard", **tab_details).__dict__)

    for tab_id, tab_details in cfg.tabs.get("staticsites").items():
        tabs.append(Tab(id=tab_id, _type="staticsite", **tab_details).__dict__)

    if vnc_clients := cfg.users.get(current_user.name).get("vnc_clients"):

        multiple = len(vnc_clients) > 1

        for index, (key, value) in enumerate(vnc_clients.items()):

            # Set landingpage to first client if "novnc" is set as landingpage
            if landingpage == "novnc" and index == 0:
                landingpage = key

            if cfg.jwt_for_vnc_access:
                additional_claims = {
                    "target": str(value.get("target")),
                    "username": str(value.get("username")),
                    "password": str(value.get("password")),
                }
                vnc_auth_token = create_access_token(identity=current_user.name, additional_claims=additional_claims)
                auth_url = f"{value.get('server')}?auth={vnc_auth_token}"
            else:
                auth_url = (
                    f"{value.get('server')}?"
                    + f"username={value.get('username')}&password={value.get('password')}&"
                    + f"target={value.get('target')}"
                )

            tab_index = (index + 1) if multiple else 0
            tabs.append(Tab(id=key, _type="client", index=tab_index, tooltip=value.get("tooltip"), url=auth_url).__dict__)

    return jsonify(tabs=tabs, landingpage=landingpage, logo=cfg.logo)


@setup_api.route("/setup/notifications", methods=["GET"])
@admin_required()
def getSetupNotifications():
    notifications = cfg.init_notifications
    return jsonify(initialNotifications=notifications)

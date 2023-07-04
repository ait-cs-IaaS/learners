from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, current_user, jwt_required
from backend.classes.Tab import Tab
from backend.conf.config import cfg
from backend.jwt_manager import admin_required

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/setup/login", methods=["GET"])
def getLoginInfo():
    return jsonify(
        headline=cfg.headline,
        welcomeText=cfg.welcomeText,
        landingpage=cfg.landingpage,
    )


@setup_api.route("/setup/styles", methods=["GET"])
def getStyles():
    return jsonify(
        logo=cfg.logo,
        theme=cfg.theme,
    )


@setup_api.route("/setup/tabs", methods=["GET"])
@jwt_required(optional=True)
def getSidebar():
    landingpage = cfg.landingpage
    base_url = request.url_root

    if not current_user:
        return jsonify(tabs=None, landingpage=landingpage, logo=cfg.logo)

    tabs = []

    # tabs.append(Tab(id="user", _type="user").__dict__)

    if current_user.admin:
        tabs.append(Tab(id="admin", _type="admin").__dict__)
        landingpage = "admin"

    for tab_id, tab_details in cfg.tabs.get("standard").items():
        tabs.append(Tab(id=tab_id, _type="standard", base_url=base_url, **tab_details).__dict__)

    for tab_id, tab_details in cfg.tabs.get("staticsites").items():
        tabs.append(Tab(id=tab_id, _type="staticsite", base_url=base_url, **tab_details).__dict__)

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
                    f"{value.get('server')}?username={value.get('username')}&password={value.get('password')}&target={value.get('target')}"
                )

            tab_index = (index + 1) if multiple else 0
            tabs.append(Tab(id=key, _type="client", base_url=base_url, index=tab_index, tooltip=value.get("tooltip"), url=auth_url).__dict__)

    return jsonify(tabs=tabs, landingpage=landingpage)


@setup_api.route("/setup/notifications", methods=["GET"])
@admin_required()
def getSetupNotifications():
    notifications = cfg.init_notifications
    return jsonify(initialNotifications=notifications)

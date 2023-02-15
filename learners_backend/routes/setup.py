from datetime import datetime, timezone
import json

from flask import Blueprint, make_response, redirect, render_template, request, jsonify
from flask_jwt_extended import create_access_token, current_user, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from learners_backend.classes.Tab import Tab
from learners_backend.conf.config import cfg

from learners_backend.logger import logger

setup_api = Blueprint("setup_api", __name__)


@setup_api.route("/setup/login", methods=["GET"])
def getLoginInfo():

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

    if not current_user:
        print("not logged in")
        return jsonify(tabs=None)

    # current_identity = get_jwt_identity()
    print("-----> Admin: {} {}".format(current_user.admin, current_user.name))
    # print(cfg.tabs)

    standard_tabs = cfg.tabs.get("standard")
    print(standard_tabs)

    tabs = []

    if current_user.admin:
        tabs.append(Tab(id="admin", _type="admin").__dict__)

    for tab_id, tab_details in cfg.tabs.get("standard").items():
        tabs.append(Tab(id=tab_id, _type="standard", **tab_details).__dict__)

    for tab_id, tab_details in cfg.tabs.get("staticsites").items():
        tabs.append(Tab(id=tab_id, _type="staticsite", **tab_details).__dict__)

    if vnc_clients := cfg.users.get(current_user.name).get("vnc_clients"):

        multiple = len(vnc_clients) > 1

        for index, (key, value) in enumerate(vnc_clients.items()):
            print(index)
            # print(client)
            # key, value = client
            print(key)
            print(value)
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

    print(tabs)

    # tabs = [tabs[1].__dict__]

    # print(tabs)

    # x = Tab("test", "icon", "tooltip", "standard", "http://...")
    # print(x)
    # y = Tab(id="documentation", _type="standard")
    # print(y)

    # staticsites_tabs = cfg.tabs.get("staticsites")
    # print(staticsites_tabs)

    # tabs = [
    #     {"id": "documentation", "type": "default", "url": "http://localhost:5000/statics/hugo/participant/en/documentation"},
    #     {"id": "exercises", "type": "default", "url": "http://localhost:5000/statics/hugo/participant/en/exercises"},
    #     {"id": "presentations", "type": "default", "url": "http://localhost:5000/statics/hugo/participant/en/presentations"},
    # ]

    return jsonify(tabs=tabs)

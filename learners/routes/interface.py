from flask import Blueprint, render_template
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt

from learners.functions.helpers import build_urls
from learners.conf.config import cfg

interface_api = Blueprint("interface_api", __name__)


@interface_api.route("/access", methods=["GET"])
@jwt_required()
def access():

    user_id = get_jwt_identity()

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=user_id)

    if vnc_clients := cfg.users.get(user_id).get("vnc_clients"):
        cfg.template["vnc_clients"] = vnc_clients
        for client, details in vnc_clients.items():
            if cfg.jwt_for_vnc_access:
                additional_claims = {
                    "target": str(details.get("target")),
                    "username": str(details.get("username")),
                    "password": str(details.get("password")),
                }
                vnc_auth_token = create_access_token(identity=user_id, additional_claims=additional_claims)
                auth_url = f"{details.get('server')}?auth={vnc_auth_token}"
            else:
                auth_url = (
                    f"{details.get('server')}?"
                    + f"username={details.get('username')}&password={details.get('password')}&"
                    + f"target={details.get('target')}"
                )
            cfg.template["vnc_clients"][client].setdefault("url", auth_url)

    return render_template("index.html", **cfg.template)

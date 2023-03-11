from datetime import datetime, timezone

from flask import Blueprint, make_response, redirect, render_template, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from backend.conf.config import cfg
from backend.conf.db_models import TokenBlocklist
from backend.database import db
from backend.functions.authentication import check_password

authentication_api = Blueprint("authentication_api", __name__)


@authentication_api.route("/login", methods=["POST"])
def postLoginData():
    data = request.get_json()

    username = data.get("username", None)
    password = data.get("password", None)

    if not check_password(cfg.users, username, password):
        return jsonify(authenticated=False)

    admin = cfg.users.get(username).get("admin")
    user_role = cfg.users.get(username).get("role")

    jwt = create_access_token(identity=username, additional_claims={"admin": admin, "role": user_role})

    return jsonify(authenticated=True, jwt=jwt), 200


# TODO: implement logout
@authentication_api.route("/logout")
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    success_msg = "Successfully logged out."
    cfg.template["authenticated"] = False
    cfg.template["vnc_clients"] = None
    cfg.template["admin"] = None
    return render_template("login.html", **cfg.template, success_msg=success_msg)


@authentication_api.route("/authentication", methods=["GET"])
@jwt_required(optional=True)
def verifyAuthentication():
    current_identity = get_jwt_identity()
    return jsonify(user=current_identity), 200

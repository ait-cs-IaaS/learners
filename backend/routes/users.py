from flask import Blueprint, redirect, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from backend.functions.database import get_all_usergroups, get_all_users
from backend.jwt_manager import admin_required
from backend.logger import logger

users_api = Blueprint("users_api", __name__)


@users_api.route("/users", methods=["GET"])
@admin_required()
def getUsers():

    db_userlist = get_all_users()
    userlist = []
    for user in db_userlist:
        userlist.append({"id": user.id, "name": user.name})

    return jsonify(users=userlist)


@users_api.route("/usergroups", methods=["GET"])
@admin_required()
def getUsergroups():

    db_usergroups = get_all_usergroups()
    grouplist = []
    for (name, ids) in db_usergroups.items():
        grouplist.append({"name": name, "ids": ids})

    return jsonify(groups=grouplist)

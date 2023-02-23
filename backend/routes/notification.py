import itertools
import json

from flask import Blueprint, jsonify, request, send_from_directory, render_template, make_response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from backend.functions.database import (
    convert_usernames_to_ids,
    db_create_notification,
    get_next_notifications_by_user,
    get_notifications_by_user,
    get_prev_notifications_by_user,
    get_usergroup_by_name,
    update_notification_link,
)

from backend.functions.helpers import build_urls, is_json
from backend.conf.config import cfg
from backend.jwt_manager import admin_required
from backend.logger import logger

notification_api = Blueprint("notification_api", __name__)


@notification_api.route("/notification/<mode>", methods=["GET"])
@jwt_required()
def get_notification(mode):

    limit = False if (mode == "last") else True
    only_new = True if (mode == "last") else False

    username = get_jwt_identity()

    notifications = []
    db_notifications, totalNotifications = get_notifications_by_user(username, limit, only_new)

    for notification in db_notifications:
        update_notification_link(notification.association_id)
        position = "all" if (mode == "force_last") else notification.position
        notifications.append({"msg": notification.msg, "position": position, "id": notification.association_id})

    return jsonify(notifications=notifications, totalNotifications=totalNotifications)


@notification_api.route("/notification/prev/<current_notification_id>", methods=["GET"])
@jwt_required()
def get_prev_notification(current_notification_id):

    username = get_jwt_identity()
    notification, totalNotifications = get_prev_notifications_by_user(username, current_notification_id)
    notifications = [{"msg": notification.msg, "position": "all", "id": notification.association_id}] if notification else []

    return jsonify(notifications=notifications, totalNotifications=totalNotifications)


@notification_api.route("/notification/next/<current_notification_id>", methods=["GET"])
@jwt_required()
def get_next_notification(current_notification_id):

    username = get_jwt_identity()
    notification, totalNotifications = get_next_notifications_by_user(username, current_notification_id)
    notifications = [{"msg": notification.msg, "position": "all", "id": notification.association_id}] if notification else []

    return jsonify(notifications=notifications, totalNotifications=totalNotifications)


@notification_api.route("/notification", methods=["POST"])
@admin_required()
def post_notification():

    try:
        formdata = request.get_json()
        users = formdata["users"]
        message = formdata["msg"]
        position = formdata["position"]

        # Get recipiennt list
        userlist = []
        for user in users:
            if is_json(user):
                json_user = json.loads(user)
                if "group" in json_user:
                    userlist.extend(get_usergroup_by_name(json_user.get("group")))
            else:
                userlist.append(user)

        usernames = [user for user in userlist if type(user) is str]
        user_ids = [user for user in userlist if type(user) is int]
        user_ids.extend(convert_usernames_to_ids(usernames))
        user_ids = list(set(user_ids))

        db_create_notification(user_ids, message, position)

        return make_response(jsonify(success=True), 200)

    except Exception as e:
        logger.exception(e)
        return make_response(jsonify(success=False, exception=e), 500)

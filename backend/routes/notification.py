import itertools
import json
import time
from backend.classes.SSE_element import SSE_element
from backend.classes.sse import sse

# from requests import Response

from flask import Blueprint, jsonify, request, send_from_directory, render_template, make_response, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, current_user
from backend.functions.database import (
    convert_usernames_to_ids,
    db_create_notification,
    get_all_notifications,
    get_last_notification,
    get_notification_by_id,
    get_notifications_by_user,
    get_usergroup_by_name,
)

from backend.functions.helpers import build_urls, convert_to_dict, is_json
from backend.conf.config import cfg
from backend.jwt_manager import admin_required, jwt_required_any_location
from backend.logger import logger

notification_api = Blueprint("notification_api", __name__)


# @notification_api.route("/notification/<mode>", methods=["GET"])
# @jwt_required()
# def get_notification(mode):

#     limit = False if (mode == "last") else True
#     only_new = True if (mode == "last") else False

#     username = get_jwt_identity()

#     notifications = []
#     # db_notifications, totalNotifications = get_notifications_by_user(username, limit, only_new)

#     # for notification in db_notifications:
#     #     update_notification_link(notification.association_id)
#     #     position = "all" if (mode == "force_last") else notification.position
#     #     notifications.append({"msg": notification.msg, "position": position, "id": notification.association_id})

#     return jsonify(notifications=notifications, totalNotifications=0)


# @notification_api.route("/notification/prev/<current_notification_id>", methods=["GET"])
# @jwt_required()
# def get_prev_notification(current_notification_id):

#     username = get_jwt_identity()
#     # notification, totalNotifications = get_prev_notifications_by_user(username, current_notification_id)
#     # notifications = [{"msg": notification.msg, "position": "all", "id": notification.association_id}] if notification else []

#     return jsonify(notifications=notifications, totalNotifications=0)


# @notification_api.route("/notification/next/<current_notification_id>", methods=["GET"])
# @jwt_required()
# def get_next_notification(current_notification_id):

#     username = get_jwt_identity()
#     # notification, totalNotifications = get_next_notifications_by_user(username, current_notification_id)
#     # notifications = [{"msg": notification.msg, "position": "all", "id": notification.association_id}] if notification else []

#     return jsonify(notifications=notifications, totalNotifications=0)


@notification_api.route("/notifications", methods=["POST"])
@admin_required()
def postNotifications():

    try:
        formdata = request.get_json()

        newNotification = SSE_element(
            recipients=formdata["recipients"],
            message=formdata["message"],
            positions=formdata["positions"],
            event="newNotification",
        )

        # Create Database entry
        db_create_notification(
            recipients=json.dumps(newNotification.recipients),
            message=newNotification.message,
            positions=json.dumps(newNotification.positions),
        )

        # Notify Users
        sse.publish(newNotification)

        return make_response(jsonify(success=True), 200)

    except Exception as e:
        logger.exception(e)
        return make_response(jsonify(success=False, exception=e), 500)


@notification_api.route("/notifications", methods=["GET"])
@jwt_required()
def getNotifications():

    db_notifications = get_notifications_by_user(current_user.id)
    notifications = convert_to_dict(db_notifications)

    print(notifications)

    return jsonify(notifications=notifications)


@notification_api.route("/stream")
@jwt_required()
def stream():
    def eventStream(user_id):

        sse_queue = sse.listen()

        while True:

            notification = sse_queue.get()

            if user_id in notification.recipients:
                msg = f"event: {notification.event}\ndata:{ notification.toJson() }\n\n"
                print("Message:", msg)
                yield msg

    return Response(eventStream(current_user.id), mimetype="text/event-stream")

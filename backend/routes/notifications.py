from backend.classes.SSE import SSE_Event, sse

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, current_user
from backend.functions.database import (
    db_create_notification,
    get_notifications_by_user,
    get_users_by_role,
)

from backend.functions.helpers import convert_to_dict
from backend.jwt_manager import admin_required
from backend.logger import logger

notifications_api = Blueprint("notifications_api", __name__)


@notifications_api.route("/notifications", methods=["POST"])
@admin_required()
def postNotifications():
    try:
        formdata = request.get_json()

        newNotification = SSE_Event(
            event="newNotification",
            message=formdata["message"],
            recipients=formdata["recipients"],
            positions=formdata["positions"],
        )

        # Create Database entry
        db_create_notification(newNotification)

        # Notify Users
        sse.publish(newNotification)

        return jsonify(success=True), 200

    except Exception as e:
        logger.exception(e)
        return jsonify(success=False, exception=e), 500


@notifications_api.route("/notifications", methods=["GET"])
@jwt_required()
def getNotifications():
    db_notifications = get_notifications_by_user(current_user.id)
    notifications = convert_to_dict(db_notifications)

    return jsonify(notifications=notifications), 200


@notifications_api.route("/notifications/ingame", methods=["POST"])
def postIngameNotifications():
    try:
        formdata = request.get_json()

        all_admins = [admin_user.id for admin_user in get_users_by_role("admin")]
        newNotification = SSE_Event(
            event="newNotification",
            message=formdata["message"],
            recipients=all_admins,
        )

        # Create Database entry
        db_create_notification(newNotification)

        # Notify Users
        sse.publish(newNotification)

        return jsonify(success=True), 200

    except Exception as e:
        logger.exception(e)
        return jsonify(success=False, exception=e), 500

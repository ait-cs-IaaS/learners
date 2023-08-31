from backend.classes.SSE import SSE_Event, sse
from flask import Blueprint, jsonify, request
from backend.functions.database import (
    db_create_notification,
    db_get_all_userids,
    db_get_page_by_id,
    db_get_page_tree,
    db_toggle_page_visibility,
)
from backend.jwt_manager import admin_required
from flask_jwt_extended import jwt_required

pages_api = Blueprint("pages_api", __name__)


@pages_api.route("/pages", methods=["GET"])
@jwt_required()
def getPages():
    pages = db_get_page_tree()
    return jsonify(pages=pages)


@pages_api.route("/pages/<page_id>/hidden", methods=["PUT"])
@admin_required()
def updatePage(page_id):
    notify = request.get_json().get("notify")
    updated = db_toggle_page_visibility(page_id)
    new_page = db_get_page_by_id(page_id)

    if not new_page.hidden and notify:
        message = """
            <h3>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6" style="width: 2rem;float: left;margin-right: 14px; margin-top: -2px;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
            Content update </h3><br>
            """
        message += f'New content: "{new_page.page_title}"'

        newNotification = SSE_Event(
            event="newNotification",
            message=message,
            recipients=db_get_all_userids(),
        )

        # Create Database entry
        db_create_notification(newNotification)

        # Notify Users
        sse.publish(newNotification)

    return jsonify(updated=updated), 200 if updated else 406

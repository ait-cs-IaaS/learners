from datetime import datetime, timezone

from flask import Blueprint, json, jsonify, request
from backend.functions.database import (
    db_get_exercise_by_id,
    db_get_submission_by_execution_uuid,
    db_update_venjix_execution,
)
from backend.functions.helpers import sse_create_and_publish
from backend.logger import logger

callback_api = Blueprint("callback_api", __name__)


@callback_api.route("/callback/<execution_uuid>", methods=["POST"])
def callback(execution_uuid):
    try:
        resp = request.get_json()
        updates = {
            "execution_uuid": execution_uuid,
            "response_timestamp": datetime.now(timezone.utc),
            "response_content": json.dumps(resp),
            "completed": bool(resp.get("returncode") == 0),
            "status_msg": resp.get("status_msg") or None,
            "script_response": resp.get("script_response") or None,
            "partial": resp.get("partial") or False,
        }

        logger.info(f"Callback for { execution_uuid } received")
        db_update_venjix_execution(updates)

        submission = db_get_submission_by_execution_uuid(execution_uuid)

        sse_create_and_publish(_type="submission", user=submission.user, exercise=submission.exercise)

        return jsonify(success=True), 200

    except Exception as e:
        logger.exception(e)
        return jsonify(success=False, exception=e), 500

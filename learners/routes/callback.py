from datetime import datetime, timezone

from flask import Blueprint, json, jsonify, make_response, request
from learners.functions.database import db_update_execution
from learners.logger import logger

callback_api = Blueprint("callback_api", __name__)


@callback_api.route("/callback/<execution_uuid>", methods=["POST"])
def callback(execution_uuid):

    try:
        resp = request.get_json()
        db_update_execution(
            execution_uuid,
            response_timestamp=datetime.now(timezone.utc),
            response_content=json.dumps(resp),
            completed=bool(resp.get("returncode") == 0),
            msg=resp.get("msg") or None,
            partial=resp.get("partial") or False,
        )
        return make_response(jsonify(success=True), 200)

    except Exception as e:
        logger.exception(e)
        return make_response(jsonify(success=False, exception=e), 500)

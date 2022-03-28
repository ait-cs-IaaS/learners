import uuid

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from learners import logger
from learners.functions.database import db_create_execution, get_current_executions, get_exercise_by_name, get_user_by_name
from learners.functions.execution import call_venjix, send_form_via_mail, update_execution_response, wait_for_response

execution_api = Blueprint("execution_api", __name__)


@execution_api.route("/execution/<type>", methods=["POST"])
@jwt_required(locations="headers")
def run_execution(type):

    username = get_jwt_identity()
    execution_uuid = f"{str(username)}_{uuid.uuid4().int & (1 << 64) - 1}"

    response = {"uuid": execution_uuid, "connected": False, "executed": False}

    data = request.get_json()
    if db_create_execution(type, data, username, execution_uuid):
        if type == "script":
            response["connected"], response["executed"] = call_venjix(username, data["script"], execution_uuid)
        if type == "form":
            response["connected"] = True
            response["executed"] = True

            if data.get("mail"):
                send_form_via_mail(username, data)

    return jsonify(response)


@execution_api.route("/execution/<exercise_name>", methods=["GET"])
@jwt_required()
def get_execution(exercise_name):

    response = {"completed": False, "executed": False, "msg": None, "response_timestamp": None, "connection_failed": False, "history": None}
    username = get_jwt_identity()

    user_id = get_user_by_name(username).id
    exercise = get_exercise_by_name(exercise_name)

    if not user_id or not exercise:
        return jsonify(response)

    last_execution, executions = get_current_executions(user_id, exercise.id)

    if last_execution:
        if exercise.type == "script" and not last_execution.response_timestamp:
            last_execution = wait_for_response(last_execution.uuid)

        response = update_execution_response(response, last_execution, executions)

    return jsonify(response)

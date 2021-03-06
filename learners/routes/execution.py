import json
import os
import uuid

from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from learners import logger
from learners.functions.database import (
    db_create_execution,
    db_create_file,
    get_completed_state,
    get_current_executions,
    get_exercise_by_name,
    get_exercise_groups,
    get_exercises_by_group,
    get_user_by_name,
)
from learners.functions.execution import call_venjix, send_form_via_mail, update_execution_response, wait_for_response
from learners.functions.helpers import allowed_file, append_key_to_dict, append_or_update_subexercise


from werkzeug.utils import secure_filename
from learners.conf.config import cfg


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

    response = {
        "completed": False,
        "executed": False,
        "msg": None,
        "response_timestamp": None,
        "connection_failed": False,
        "history": None,
        "partial": False,
    }
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


@execution_api.route("/execution-state", methods=["GET"])
@jwt_required()
def get_execution_state():

    username = get_jwt_identity()
    user = get_user_by_name(username)
    parent_names = get_exercise_groups()

    results = {}

    for parent_name in parent_names:
        subexercises = get_exercises_by_group(parent_name)

        for subexercise in subexercises:
            parent = parent_name or subexercise.page_title
            results = append_key_to_dict(results, parent, {"total": 0, "done": 0, "exercises": []})

            done = int(any(state[0] for state in get_completed_state(user.id, subexercise.id)))
            exerciseobj = {"title": subexercise.page_title, "total": 1, "done": done}
            results[parent] = append_or_update_subexercise(results[parent], exerciseobj)

    return jsonify(success_list=results)


@execution_api.route("/upload", methods=["POST"])
@jwt_required(locations="headers")
def upload_file():

    response = {
        "completed": False,
        "executed": False,
        "msg": None,
        "file": None,
    }

    if "file" not in request.files:
        response["msg"] = "file missing"
        return jsonify(response)

    file = request.files["file"]

    if file.filename == "":
        response["msg"] = "no file selected"
        return jsonify(response)

    username = get_jwt_identity()

    if file:
        filename = f"{username}_{secure_filename(file.filename)}"
        if not allowed_file(filename):
            response["msg"] = "file type not allowed"
            return jsonify(response)
        try:
            file.save(os.path.join(cfg.upload_folder, filename))
            filehash = db_create_file(filename, get_jwt_identity())
            response["completed"] = True
            response["executed"] = True
            response["msg"] = "file sucessfully uploaded"
            response["file"] = filehash

        except Exception as e:
            response["msg"] = "server error"

    return jsonify(response)


@execution_api.route("/upload/<name>")
@jwt_required()
def download_file(name):
    return send_from_directory(cfg.upload_folder, name)

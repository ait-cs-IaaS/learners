import os
import uuid
from backend.classes.SubmissionResponse import SubmissionResponse

from flask import Blueprint, jsonify, request, send_from_directory, make_response
from flask_jwt_extended import jwt_required, current_user
from backend.jwt_manager import admin_required, only_self_or_admin
from backend.logger import logger
from backend.functions.database import (
    db_create_submission,
    db_create_file,
    db_get_current_submissions,
    db_get_current_submissions,
    db_get_exercise_by_id,
    db_get_running_executions_by_name,
    db_get_all_exercises,
    db_get_all_users,
    db_get_completed_state,
    db_get_submission_by_exercise_id,
    db_get_submissions_by_user_exercise,
    db_get_exercise_groups,
    db_get_exercises_by_group,
    db_get_submissions_by_user_exercise,
    db_get_time,
    db_get_user_by_id,
    db_set_time,
)
from backend.functions.execution import (
    call_venjix,
    wait_for_venjix_response,
)
from backend.functions.helpers import allowed_file, append_key_to_dict, append_or_update_subexercise, convert_to_dict, sse_create_and_publish


from werkzeug.utils import secure_filename
from backend.conf.config import cfg


executions_api = Blueprint("executions_api", __name__)


@executions_api.route("/submissions", methods=["GET"])
@admin_required()
def getAllSubmissions():
    submissions = []

    for user in db_get_all_users():
        executions = {"user_id": user.id, "username": user.name}
        for exercise in db_get_all_exercises():
            # completed_state = [state[0] for state in db_get_completed_state(user.id, exercise.id)]
            _submissions = db_get_submissions_by_user_exercise(user.id, exercise.id)
            execution_ids = [execution.get("id") for execution in convert_to_dict(_submissions)]
            executions[exercise.id] = {
                # "completed": int(any(completed_state)) if completed_state else -1,
                "completed": int(_submissions[0].completed) if _submissions and _submissions[0] else 0,
                "executed": int(_submissions[0].executed) if _submissions and _submissions[0] else 0,
                "executions": execution_ids,
            }
        submissions.append(executions)

    return jsonify(submissions=submissions)


@executions_api.route("/submissions/form/<exercise_id>", methods=["POST"])
@jwt_required()
def postFormSubmission(exercise_id):
    response = SubmissionResponse()

    data = request.get_json()
    if db_create_submission("form", exercise_id, current_user.id, data=data):
        response.executed = True
        response.completed = True

    sse_create_and_publish(_type="submission", user=current_user, exercise=db_get_exercise_by_id(exercise_id))

    return jsonify(response.__dict__)


@executions_api.route("/submissions/script/<exercise_id>", methods=["POST"])
@jwt_required()
def postScriptSubmission(exercise_id):
    execution_uuid = f"{str(current_user.name)}_{uuid.uuid4().int & (1 << 64) - 1}"
    response = SubmissionResponse(uuid=execution_uuid)
    callback_url = f"{request.headers.get('Referer').split('/statics')[0]}/callback"

    if db_create_submission("script", exercise_id, current_user.id, execution_uuid=execution_uuid):
        response.connected, response.executed = call_venjix(exercise_id, current_user.name, callback_url, execution_uuid)

    return jsonify(response.__dict__)


@executions_api.route("/submissions/<exercise_id>", methods=["GET"])
@jwt_required()
def getExerciseSubmissions(exercise_id):
    response = None

    if submissions := db_get_current_submissions(current_user.id, exercise_id):
        response = SubmissionResponse()
        response.update(convert_to_dict(submissions))
        response = response.__dict__

    return jsonify(response)


@executions_api.route("/submissions/<user_id>/<exercise_id>", methods=["GET"])
@only_self_or_admin()
def getExerciseSubmissionsByUser(user_id, exercise_id):
    exercise = db_get_exercise_by_id(exercise_id)
    db_submissions = db_get_submissions_by_user_exercise(user_id, exercise.id)

    return jsonify(
        exercise_name=exercise.exercise_name, user_name=db_get_user_by_id(user_id).name, submissions=convert_to_dict(db_submissions)
    )


@executions_api.route("/executions/<exercise_id>", methods=["GET"])
@jwt_required()
def getExecutions(exercise_id):
    response = None

    if executions := db_get_current_submissions(current_user.id, exercise_id):
        response = SubmissionResponse()
        response.update(convert_to_dict(executions))
        response = response.__dict__

    return jsonify(response)


@executions_api.route("/executions/state/<execution_uuid>", methods=["GET"])
@jwt_required()
def getExecutionState(execution_uuid):
    response = SubmissionResponse()
    venjix_response = wait_for_venjix_response(execution_uuid)
    response.update(venjix_response)
    response = response.__dict__

    return jsonify(response)


@executions_api.route("/executions/active/<script_name>", methods=["GET"])
@jwt_required()
def getActiveExecutionsState(script_name):
    response = None

    if running_execution := db_get_running_executions_by_name(current_user.id, script_name):
        response = SubmissionResponse()
        execution_uuid = running_execution[0].get("execution_uuid")
        venjix_response = wait_for_venjix_response(execution_uuid)
        response.update(venjix_response)
        response = response.__dict__

    return jsonify(response)


@executions_api.route("/progress", methods=["GET"])
@jwt_required()
def getCurrentExerciseState():
    parent_names = db_get_exercise_groups()
    results = {}

    for parent_name in parent_names:
        subexercises = db_get_exercises_by_group(parent_name)

        for subexercise in subexercises:
            parent = parent_name or subexercise.page_title
            results = append_key_to_dict(results, parent, {"total": 0, "done": 0, "exercises": []})

            done = int(any(state[0] for state in db_get_completed_state(current_user.id, subexercise.id)))
            exerciseobj = {"title": subexercise.page_title, "total": 1, "done": done}
            results[parent] = append_or_update_subexercise(results[parent], exerciseobj)

    return jsonify(success_list=results)


@executions_api.route("/uploads", methods=["POST"])
@jwt_required()
def uploadFile():
    # Create an object of SubmissionResponse class
    response = SubmissionResponse()

    # Check if 'file' is in the request.files dictionary, else return error message
    if "file" not in request.files:
        response.status_msg = "File missing"
        return jsonify(response.__dict__)

    # If filename is empty, return error message
    file = request.files["file"]
    if file.filename == "":
        response.status_msg = "No file selected"
        return jsonify(response.__dict__)

    # Generate a new file name and check if the file type is allowed, else return error message
    filename = f"{current_user.name}_{secure_filename(file.filename)}"
    if not allowed_file(filename):
        response.status_msg = "File type not allowed"
        return jsonify(response.__dict__)

    try:
        # Save the file to the upload folder and create a filehash for it in the database
        file.save(os.path.join(os.getcwd(), cfg.upload_folder, filename))
        db_create_file(filename, current_user.id)

        # Update the response object with success status and other details
        response.completed = True
        response.executed = True
        response.status_msg = "File successfully uploaded"
        response.filename = filename

    # Catch any server errors and return error message
    except Exception as e:
        logger.exception(f"ERROR: {e}")
        response.status_msg = "Server error"

    # Return the JSON representation of the response object
    return jsonify(response.__dict__)


@executions_api.route("/uploads/<filename>", methods=["GET"])
@jwt_required()
def downloadFile(filename):
    return send_from_directory(os.path.join(os.getcwd(), cfg.upload_folder), filename)


@executions_api.route("/time", methods=["GET"])
@admin_required()
def getTime():
    if stored_time := db_get_time():
        return jsonify(convert_to_dict(stored_time))
    return jsonify({})


@executions_api.route("/time/<action>", methods=["POST"])
@admin_required()
def setTimer(action):

    offset = 0

    if request.is_json:
        offset = (request.get_json()).get("offset", 0)

    if timer_event := db_set_time(action, offset):
        sse_create_and_publish(_type="timer", timer=convert_to_dict(timer_event))
        return jsonify(updated=True)

    else:
        return jsonify(updated=False)

import json

from flask import Blueprint, jsonify, render_template
from learners.conf.config import cfg
from learners.functions.database import (
    get_all_exercises,
    get_all_users,
    get_executions_by_user_exercise,
    get_exercise_by_name,
    get_user_by_id,
)
from learners.functions.helpers import extract_history
from learners.functions.results import construct_results_table
from learners.jwt_manager import admin_required
from learners.logger import logger

admin_api = Blueprint("admin_api", __name__)


@admin_api.route("/admin", methods=["GET"])
@admin_required()
def admin_area():

    exercises = get_all_exercises()
    users = get_all_users()

    user_filter = [{"id": 0, "username": "all"}]
    user_filter.extend({"id": user.id, "username": user.name} for user in users)

    exercises_filter = [{"id": "all", "name": "all"}]
    exercises_filter.extend({"id": exercise.exercise_name, "name": exercise.page_title} for exercise in exercises)

    results_table = construct_results_table(exercises, users)
    return render_template("results.html", exercises=exercises_filter, users=user_filter, table=results_table, **cfg.template)


@admin_api.route("/result/<user_id>/<exercise_name>", methods=["GET"])
@admin_required()
def get_exercise_result(user_id, exercise_name):

    exercise = get_exercise_by_name(exercise_name)
    user = get_user_by_id(user_id)
    executions = get_executions_by_user_exercise(user_id, exercise.id)

    last_execution = executions[0] if executions else None
    data = {
        "completed": any(execution.completed for execution in executions) if last_execution else False,
        "executed": any(not execution.connection_failed for execution in executions) if last_execution else False,
        "msg": last_execution.msg if last_execution else None,
        "response_timestamp": last_execution.response_timestamp if last_execution else None,
        "connection": any(not execution.connection_failed for execution in executions) if last_execution else False,
    }

    if exercise.type == "form":
        data["form"] = json.loads(last_execution.form_data) if last_execution else None

    data["history"] = extract_history(executions) if executions else None

    return render_template("result_details.html", user=user.name, exercise=exercise.title, data=data, **cfg.template)

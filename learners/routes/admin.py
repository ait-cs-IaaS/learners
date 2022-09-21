import json

from flask import Blueprint, jsonify, render_template
from collections import defaultdict
from learners.conf.config import cfg
from learners.functions.database import (
    get_all_exercises,
    get_all_exercises_sorted,
    get_all_questionaires_sorted,
    get_all_users,
    get_executions_by_user_exercise,
    get_user_by_id,
    get_completion_percentage,
    get_questionaire_completion_percentage,
    get_exercise_by_global_exercise_id,
    get_results_of_single_exercise,
    get_questionaire_by_global_questionaire_id,
    get_all_questionaires_questions,
    get_question_counts,
)
from learners.functions.helpers import extract_history, replace_attachhment_with_url, build_urls
from learners.functions.results import construct_results_table
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from learners.jwt_manager import admin_required
from learners.logger import logger
from learners.conf.config import cfg

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

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
    return render_template("results.html", exercises=exercises_filter, users=user_filter, table=results_table, **cfg.template)


@admin_api.route("/result/all", methods=["GET"])
@admin_required()
def get_all_results():

    grouped_exercises = {}
    sorted_exercises = get_all_exercises_sorted()

    for exercise in sorted_exercises:
        setattr(exercise, "completion_percentage", get_completion_percentage(exercise.id))
        if not grouped_exercises.get(exercise.parent_page_title):
            grouped_exercises[exercise.parent_page_title] = {exercise.page_title: [exercise]}
        elif grouped_exercises[exercise.parent_page_title].get(exercise.page_title):
            grouped_exercises[exercise.parent_page_title][exercise.page_title].append(exercise)

        else:
            grouped_exercises[exercise.parent_page_title][exercise.page_title] = [exercise]

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
    return render_template("results_overview.html", exercises=grouped_exercises, **cfg.template)


@admin_api.route("/result/<global_exercise_id>", methods=["GET"])
@admin_required()
def get_single_result(global_exercise_id):

    exercise = get_exercise_by_global_exercise_id(global_exercise_id)
    setattr(exercise, "completion_percentage", get_completion_percentage(exercise.id))

    results = get_results_of_single_exercise(global_exercise_id)

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
    return render_template("results_single.html", exercise=exercise, results=results, **cfg.template)


@admin_api.route("/result/<user_id>/<global_exercise_id>", methods=["GET"])
@admin_required()
def get_exercise_result(user_id, global_exercise_id):

    exercise = get_exercise_by_global_exercise_id(global_exercise_id)
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

    if exercise.exercise_type == "form":
        data["form"] = json.loads(last_execution.form_data) if last_execution else None
        data["form"] = replace_attachhment_with_url(data["form"])

    data["history"] = extract_history(executions) if executions else None

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
    return render_template("results_execution_details.html", user=user.name, exercise=exercise.exercise_name, data=data, **cfg.template)


@admin_api.route("/questionaire/all", methods=["GET"])
@admin_required()
def get_all_questionaires():

    grouped_questionaires = {}
    sorted_questionaires = get_all_questionaires_sorted()

    for questionaire in sorted_questionaires:
        setattr(questionaire, "completion_percentage", get_questionaire_completion_percentage(questionaire.global_questionaire_id))

        if not grouped_questionaires.get(questionaire.parent_page_title):
            grouped_questionaires[questionaire.parent_page_title] = [questionaire]
        else:
            grouped_questionaires[questionaire.parent_page_title].append(questionaire)

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
    return render_template("questionaires_overview.html", questionaires=grouped_questionaires, **cfg.template)


@admin_api.route("/questionaire/<global_questionaire_id>", methods=["GET"])
@admin_required()
def get_single_questionaire(global_questionaire_id):

    # questionaire = get_exercise_by_global_exercise_id(global_questionaire_id)
    questionaire = get_questionaire_by_global_questionaire_id(global_questionaire_id)
    setattr(questionaire, "completion_percentage", get_questionaire_completion_percentage(questionaire.global_questionaire_id))
    questions = get_all_questionaires_questions(global_questionaire_id)

    for question in questions:
        labels, counts = get_question_counts(question.global_question_id)
        setattr(question, "labels", labels)
        setattr(question, "counts", counts)

    cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
    return render_template("questionaires_single.html", questionaire=questionaire, questions=questions, **cfg.template)

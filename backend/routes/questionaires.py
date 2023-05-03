import json
from backend.classes.SSE import SSE_Event, sse
from backend.jwt_manager import admin_required

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, current_user
from backend.functions.database import (
    db_activate_questioniare_question,
    db_create_questionaire_answer,
    db_get_questionaire_question_answers_by_user,
    get_all_userids,
    get_grouped_questionaires,
    get_questionaire_question_by_global_question_id,
    get_questionaire_results_by_global_question_id,
    get_users_by_role,
)

from backend.functions.helpers import convert_to_dict, sse_create_and_publish
from backend.logger import logger

questionaires_api = Blueprint("questionaires_api", __name__)


@questionaires_api.route("/questionaires", methods=["GET"])
@admin_required()
def getQuestionaires():
    grouped_questionaires = get_grouped_questionaires()
    return jsonify(questionaires=grouped_questionaires), 200


@questionaires_api.route("/questionaires/questions", methods=["GET"])
@jwt_required()
def getQuestions():
    grouped_questionaires = get_grouped_questionaires()

    active_questions = []

    # Filter for active questions
    for questionaire in grouped_questionaires:
        for question in questionaire.get("questions"):
            question["global_questionaire_id"] = questionaire.get("global_questionaire_id")
            question["page_title"] = questionaire.get("page_title")
            if question.get("active"):
                # Check if user has already answerd the questionaire
                answers = db_get_questionaire_question_answers_by_user(question["global_question_id"], current_user.id)
                if not len(answers):
                    active_questions.append(question)

    return jsonify(questions=active_questions), 200


# Activate Question
@questionaires_api.route("/questionaires/questions/<global_question_id>", methods=["PUT"])
@admin_required()
def activateQuestion(global_question_id):
    if question := db_activate_questioniare_question(global_question_id=global_question_id):
        user_list = get_all_userids()

        # Send SSE event
        newQuestionaire = SSE_Event(
            event="newQuestionaire",
            question=question,
            recipients=user_list,
        )

        # Notify Users
        sse.publish(newQuestionaire)

        return jsonify(success=True), 200

    return jsonify(success=False), 500


@questionaires_api.route("/questionaires/questions/<global_question_id>", methods=["POST"])
@jwt_required()
def submitQuestion(global_question_id):
    data = request.get_json()
    answers = data.get("answers")

    if db_create_questionaire_answer(global_question_id=global_question_id, answers=answers, user_id=current_user.id):
        # Send SSE event
        newQuestionaire = SSE_Event(
            event="newQuestionaireSubmission",
            question=global_question_id,
            recipients=[admin_user.id for admin_user in get_users_by_role("admin")],
        )

        # Notify Users
        sse.publish(newQuestionaire)

        return jsonify(success=True), 200

    return jsonify(success=False), 500


@questionaires_api.route("/questionaires/questions/<global_question_id>", methods=["GET"])
@admin_required()
def getQuestionaireResults(global_question_id):
    labels, results = get_questionaire_results_by_global_question_id(global_question_id)
    question = get_questionaire_question_by_global_question_id(global_question_id).question

    return jsonify(question=question, labels=labels, results=results), 200

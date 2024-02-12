from backend.jwt_manager import admin_required

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from backend.functions.database import (
    db_activate_questioniare_question,
    db_create_questionnaire_answer,
    db_get_participants_userids,
    db_get_questionnaire_question_answers_by_user,
    db_get_grouped_questionnaires,
    db_get_questionnaire_question_by_question_id,
    db_get_questionnaire_results_by_question_id,
    db_get_admin_users,
)
from backend.functions.helpers import sse_create_and_publish

questionnaires_api = Blueprint("questionnaires_api", __name__)


@questionnaires_api.route("/questionnaires", methods=["GET"])
@admin_required()
def getQuestionnaires():
    grouped_questionnaires = db_get_grouped_questionnaires()
    return jsonify(questionnaires=grouped_questionnaires), 200


@questionnaires_api.route("/questionnaires/questions", methods=["GET"])
@jwt_required()
def getQuestions():
    grouped_questionnaires = db_get_grouped_questionnaires()

    active_questions = []

    # Avoid promting admins
    if current_user.role == "instructor":
        return jsonify(questions=[]), 200

    # Filter for active questions
    for questionnaire in grouped_questionnaires:
        for question in questionnaire.get("questions"):
            question["questionnaire_id"] = questionnaire.get("questionnaire_id")
            question["page_title"] = questionnaire.get("page_title")
            if question.get("active"):
                # Check if user has already answerd the questionnaire
                answers = db_get_questionnaire_question_answers_by_user(question["question_id"], current_user.id)
                if not len(answers):
                    active_questions.append(question)

    return jsonify(questions=active_questions), 200


# Activate Question
@questionnaires_api.route("/questionnaires/questions/<question_id>", methods=["PUT"])
@admin_required()
def activateQuestion(question_id):
    if question := db_activate_questioniare_question(question_id=question_id):
        user_list = db_get_participants_userids()

        sse_create_and_publish(
            event="questionnaire",
            question=question,
            recipients=user_list,
        )

        return jsonify(success=True), 200

    return jsonify(success=False), 500


@questionnaires_api.route("/questionnaires/questions/<question_id>", methods=["POST"])
@jwt_required()
def submitQuestion(question_id):
    data = request.get_json()
    answers = data.get("answers")

    if db_create_questionnaire_answer(question_id=question_id, answers=answers, user_id=current_user.id):
        # Send SSE event
        sse_create_and_publish(
            event="questionnaireSubmission",
            question=question_id,
            recipients=[admin_user.id for admin_user in db_get_admin_users()],
        )

        return jsonify(success=True), 200

    return jsonify(success=False), 500


@questionnaires_api.route("/questionnaires/questions/<question_id>", methods=["GET"])
@admin_required()
def getQuestionnaireResults(question_id):
    labels, results = db_get_questionnaire_results_by_question_id(question_id)
    question = db_get_questionnaire_question_by_question_id(question_id).question

    return jsonify(question=question, labels=labels, results=results), 200

import json
from backend.classes.SSE import SSE_Event, sse
from backend.jwt_manager import admin_required

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, current_user
from backend.functions.database import (
    db_activate_questioniare_question,
    db_create_questionaire_answer,
    get_all_questionaires_sorted,
    get_all_userids,
    get_grouped_questionaires,
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
        return jsonify(success=True), 200

    return jsonify(success=False), 500

    # grouped_questionaires = get_grouped_questionaires()

    # active_questions = []

    # # Filter for active questions
    # for questionaire in grouped_questionaires:
    #     for question in questionaire.get("questions"):
    #         question["global_questionaire_id"] = questionaire.get("global_questionaire_id")
    #         question["page_title"] = questionaire.get("page_title")
    #         if question.get("active"):
    #             active_questions.append(question)

    # return jsonify(success=True), 200


# @questionaires_api.route("/questionaires/<global_questionaire_id>", methods=["GET"])
# @jwt_required()
# def getQuestionairesById(global_questionaire_id):

#     grouped_questionaires = {}
#     sorted_questionaires = convert_to_dict(get_all_questionaires_sorted())
#     print(sorted_questionaires)
#     print(global_questionaire_id)

#     # example = [{"id": 1, "question": "testquestion", "multiple": True, "answers": ["answer 1", "answer 2"]}]

#     return jsonify(questionaires=sorted_questionaires), 200

#     # for questionaire in sorted_questionaires:
#     #     setattr(questionaire, "completion_percentage", get_questionaire_completion_percentage(questionaire.global_questionaire_id))

#     #     if not grouped_questionaires.get(questionaire.parent_page_title):
#     #         grouped_questionaires[questionaire.parent_page_title] = [questionaire]
#     #     else:
#     #         grouped_questionaires[questionaire.parent_page_title].append(questionaire)

#     # cfg.template = build_urls(config=cfg, role=get_jwt().get("role"), user_id=get_jwt_identity())
#     # return render_template("questionaires_overview.html", questionaires=grouped_questionaires, **cfg.template)

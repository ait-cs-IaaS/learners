from flask import Blueprint, jsonify, make_response, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from learners.functions.database import (
    db_create_comment,
    get_all_comments,
    get_exercise_by_global_exercise_id,
    get_user_by_id,
)

from learners.conf.config import cfg
from learners.jwt_manager import admin_required


comment_api = Blueprint("comment_api", __name__)


@comment_api.route("/comment", methods=["POST"])
@jwt_required(locations="headers")
def run_execution():

    username = get_jwt_identity()
    data = request.get_json()

    if db_create_comment(data, username):
        return make_response(jsonify(success=True), 200)

    return make_response(jsonify(success=False), 500)


@comment_api.route("/comments", methods=["GET"])
@admin_required()
def comments_overview():

    all_comments = get_all_comments()
    comments_dict = {}

    for comment in all_comments:
        exercise_name = get_exercise_by_global_exercise_id(comment.global_exercise_id).page_title
        comment_dict = {"user": get_user_by_id(comment.user_id).name, "comment": comment.comment}
        if not comments_dict.get(exercise_name):
            comments_dict[exercise_name] = []
        comments_dict[exercise_name].append(comment_dict)

    return render_template("comments.html", comments=comments_dict, **cfg.template)

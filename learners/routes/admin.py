from datetime import timezone

from flask import Blueprint, jsonify, render_template
from learners.database import User, get_exercises
from learners.jwt_manager import admin_required
from learners.logger import logger

admin_api = Blueprint("admin_api", __name__)

exercises = get_exercises()


@admin_api.route("/admin", methods=["GET"])
@admin_required()
def admin_area():

    return jsonify(WIP=True)
    # executions = []

    # user_list = [{"id": 0, "username": "all"}]
    # users = User.query.all()

    # for user in users:

    #     user_list.append({"id": user.id, "username": user.username})
    #     execution = {"user_id": user.id, "username": user.username}

    #     for exercise in exercises[1:]:
    #         exercise_name = exercise["id"]
    #         exercise_type = exercise["type"]
    #         execution[exercise_name] = -1

    #         if exercise_type == "form":
    #             for exec in user.formExercises:
    #                 if exec.name == exercise_name:
    #                     execution[exercise_name] = 1

    #         elif exercise_type == "script":
    #             for exec in user.scriptExercises:
    #                 if exec.script_name == exercise["script"]:
    #                     execution[exercise_name] = exec.completed

    #     executions.append(execution)

    # columns = [{"name": "id", "id": "user_id"}, {"name": "user", "id": "username"}]
    # columns.extend({"name": exercise["name"], "id": exercise["id"]} for exercise in exercises[1:])

    # return render_template("results.html", exercises=exercises, users=user_list, table={"columns": columns, "data": executions})


@admin_api.route("/results/<user_id>/<exercise_id>", methods=["GET"])
@admin_required()
def get_exercise_results(user_id, exercise_id):

    return jsonify(WIP=True)

    # exercise = next(exercise for exercise in exercises if exercise["id"] == exercise_id)
    # exercise_type = exercise["type"]
    # data = None

    # try:
    #     username = User.query.filter_by(id=user_id).first().username
    # except:
    #     logger.warn("User not found.")

    # try:
    #     if exercise_type == "form":
    #         data = json.loads(FormExercise.query.filter_by(user_id=user_id).filter_by(name=exercise["id"]).first().data)
    #     elif exercise_type == "script":
    #         executed, completed, history = get_history_from_DB(exercise["script"], username)
    #         data = {"executed": executed, "completed": completed, "history": history}
    #     else:
    #         return jsonify(error="Exercise type unknown.")
    # except:
    #     logger.warn("No data found.")

    # return render_template("results_details.html", user=username, exercise=exercise["name"], data=data)

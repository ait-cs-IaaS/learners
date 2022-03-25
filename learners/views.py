from datetime import timezone
from flask import json
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import request
from flask import Blueprint
from flask import send_from_directory
from flask import abort

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from flask_mail import Message

import requests
import uuid
import time
from datetime import datetime
from datetime import timedelta
import logging

from learners.helpers import (
    db_create_execution,
    get_history_from_DB,
    check_password,
    is_admin,
    connection_failed,
    call_venjix,
    send_form_via_mail,
)
from learners.database import Execution, Exercise, User, ScriptExercise, FormExercise, TokenBlocklist, get_exercises
from learners.conf.config import cfg
from learners.database import db
from learners.mail_manager import mail
from learners.jwt_manager import admin_required
from learners.logger import logger


bp = Blueprint("views", __name__)
exercises = get_exercises()


@bp.route("/")
def home():

    try:
        verify_jwt_in_request()
        return redirect("/admin") if get_jwt().get("is_admin") else redirect("/access")

    except:
        logger.info("No valid token present.")
        return redirect("/login")


@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        try:
            verify_jwt_in_request()
            success_msg = f"Logged in as {get_jwt_identity()}."
            return render_template("login.html", **cfg.template, success=True, success_msg=success_msg)
        except:
            return render_template("login.html", **cfg.template)

    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if not check_password(cfg.users, username, password):
        error_msg = "Invalid username or password"
        return render_template("login.html", **cfg.template, error=error_msg)

    access_token = create_access_token(identity=username, additional_claims={"is_admin": is_admin(username)})
    response = redirect("/admin") if is_admin(username) else redirect("/access")
    response.set_cookie("auth", value=access_token, secure=True, httponly=False)

    return response


@bp.route("/logout")
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    success_msg = "Successfully logged out."
    return render_template("login.html", **cfg.template, success_msg=success_msg)


@bp.route("/access")
@jwt_required()
def access():

    user_id = get_jwt_identity()

    if vnc_clients := cfg.users.get(user_id).get("vnc_clients"):
        for client, details in vnc_clients.items():
            if cfg.jwt_for_vnc_access:
                additional_claims = {
                    "target": str(details.get("target")),
                    "username": str(details.get("username")),
                    "password": str(details.get("password")),
                }
                vnc_auth_token = create_access_token(identity=user_id, additional_claims=additional_claims)
                auth_url = f"{details.get('server')}?auth={vnc_auth_token}"
            else:
                auth_url = (
                    f"{details.get('server')}?"
                    + f"username={details.get('username')}&password={details.get('password')}&"
                    + f"target={details.get('target')}"
                )
            cfg.template["vnc_clients"][client].setdefault("url", auth_url)

    return render_template("index.html", **cfg.template)


# POST exercise -> if type script
#                -> if type form
# GET exercise -> if response or fail in last db else:
#               -> loop ("monitor")


@bp.route("/execution/<type>", methods=["POST"])
@jwt_required()
def run_execution(type):

    print("execute")

    user = get_jwt_identity()
    execution_uuid = f"{str(user)}_{uuid.uuid4().int & (1 << 64) - 1}"

    response = {"uuid": execution_uuid, "connected": False, "executed": False}

    data = request.get_json()
    if db_create_execution(type, data, user, execution_uuid):
        if type == "script":
            response["connected"], response["executed"] = call_venjix(user, data["script"], execution_uuid)
        if type == "form":
            response["connected"] = True
            response["executed"] = True

            if request.data.get("mail"):
                send_form_via_mail(user, data)

    print(response)
    return jsonify(response)


@bp.route("/execution/<id>", methods=["GET"])
@jwt_required()
def get_execution(id):

    print("call")
    user = get_jwt_identity()
    print(user)

    return jsonify(id=id)


@bp.route("/execute/<script>", methods=["POST"])
# @jwt_required()
def call_venjix_old(script):

    # get user id from JWT token
    verify_jwt_in_request(locations="headers")
    user_jwt_identity = get_jwt_identity()

    # generate uuid
    call_uuid = f"{str(user_jwt_identity)}_{uuid.uuid4().int & (1 << 64) - 1}"

    try:
        user_id = User.query.filter_by(username=user_jwt_identity).first().id

        new_entry = ScriptExercise(script_name=script, call_uuid=call_uuid, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()

        # send POST request
        response = requests.post(
            url=f"{cfg.venjix.get('url')}/{script}",
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {cfg.venjix.get('auth_secret')}",
            },
            data=json.dumps(
                {
                    "script": script,
                    "user_id": user_jwt_identity,
                    "callback": f"{cfg.callback.get('endpoint')}/{str(call_uuid)}",
                }
            ),
        )

        # get response
        init_state = response.json()
        executed = bool(init_state["response"] == "script started")

        return jsonify(uuid=call_uuid, executed=executed)

    except Exception as connection_exception:

        try:
            db_entry = ScriptExercise.query.filter_by(call_uuid=call_uuid).first()
            db_entry.msg = "Connection failed."
            db_entry.connection_failed = True
            db.session.commit()
        except Exception as database_exception:
            logger.exception(database_exception)

        logger.exception(connection_exception)

    return jsonify(uuid=call_uuid, executed=False)


@bp.route("/history/<script>")
@jwt_required()
def get_history(script):

    executed, completed, history = get_history_from_DB(script, get_jwt_identity())

    if executed and history:
        return jsonify(
            executed=executed,
            completed=completed,
            history=history,
        )
    elif history:
        return jsonify(
            never_executed=True,
            history=history,
        )
    else:
        return jsonify(never_executed=True)


@bp.route("/monitor/<call_uuid>")
@jwt_required()
def monitor(call_uuid):

    while True:
        time.sleep(0.5)

        db_entry = ScriptExercise.query.filter_by(call_uuid=call_uuid).first()

        if db_entry is None:
            return jsonify(completed=False)
        elif db_entry.response_time != None:
            _, _, history = get_history_from_DB(db_entry.script_name, get_jwt_identity())
            return jsonify(completed=db_entry.completed, msg=db_entry.msg, history=history)
        elif db_entry.connection_failed == True:
            _, _, history = get_history_from_DB(db_entry.script_name, get_jwt_identity())
            return jsonify(completed=False, msg="no response", history=history)

        # force new query on db in the next iteration
        db.session.close()


@bp.route("/form/<form_name>", methods=["GET", "POST"])
@jwt_required()
def get_formdata(form_name):

    # Get user identification
    verify_jwt_in_request(locations="headers")
    user_jwt_identity = get_jwt_identity()

    try:
        user_id = User.query.filter_by(username=user_jwt_identity).first().id

        # Check whether the form was already submitted
        prio_submission = db.session.query(FormExercise).filter_by(user_id=user_id).filter_by(name=form_name).first()

        if request.method == "GET":

            if prio_submission is not None:
                return jsonify(executed=True, completed=True)
            else:
                return jsonify(never_executed=True)

        if request.method == "POST":

            if prio_submission is not None:
                return jsonify(completed=False, msg="Form was already submitted.")

            form_data = json.dumps(request.form.to_dict(), indent=4, sort_keys=False)

            # Create database entry
            new_form = FormExercise(
                user_id=user_id,
                name=form_name,
                data=form_data,
                timestamp=datetime.now(timezone.utc),
            )

            db.session.add(new_form)
            db.session.commit()

            # if specified, send form data via email
            if request.headers.get("Method") == "mail":
                subject = f"Form Submission: {user_jwt_identity} - {form_name}"

                mailbody = "<h1>Results</h1>" + "<h2>Information:</h2>"
                mailbody += f"<strong>User:</strong> {user_jwt_identity}</br>"
                mailbody += f"<strong>Form:</strong> {form_name}</br>"
                mailbody += "<h2>Data:</h2>"

                data = ""
                for (key, value) in request.form.to_dict().items():
                    if not value:
                        value = "<i>-- emtpy --</i>"
                    data += f"<strong>{key}</strong>: {value}</br>"

                mailbody += f"<p>{data}</p></br>"

                msg = Message(subject, sender=("Venjix", "lenhard.reuter@e-caterva.com"), recipients=["lenhard.reuter@ait.ac.at"])
                msg.html = mailbody
                mail.send(msg)

            return jsonify(executed=True)

    except:
        return jsonify(executed=False, completed=False, msg="Failed to find user in database. Please login again.")


@bp.route("/callback/<call_uuid>", methods=["POST"])
def callback(call_uuid):

    feedback = request.get_json()

    db_entry = ScriptExercise.query.filter_by(call_uuid=call_uuid).first()
    db_entry.response_time = datetime.now(timezone.utc)
    db_entry.response_content = json.dumps(feedback)
    db_entry.completed = int(feedback.get("returncode") == 0)
    db_entry.msg = feedback.get("msg") or None
    db.session.commit()

    return jsonify(completed=True)


@bp.route("/documentation/", methods=["GET"])
@bp.route("/documentation", methods=["GET"])
@jwt_required()
def serve_documentation_index():
    try:
        path = f"{cfg.documentation.get('directory')}/{get_jwt_identity()}/"
        return send_from_directory(path, "index.html")
    except Exception as e:
        logger.exception(f"Loading documentation from {cfg.documentation.get('directory')} failed")
        abort(e)


@bp.route("/documentation/<path:path>", methods=["GET"])
@jwt_required()
def serve_documentation(path):
    try:
        path = f"{path}index.html" if path.endswith("/") else path
        full_path = f"{get_jwt_identity()}/{path}"
        return send_from_directory(cfg.documentation.get("directory"), full_path)
    except Exception as e:
        logger.exception(f"Loading documentation from {cfg.documentation.get('directory')} failed")
        abort(e)


@bp.route("/exercises/", methods=["GET"])
@bp.route("/exercises", methods=["GET"])
@jwt_required()
def serve_exercises_index():
    try:
        path = f"{cfg.exercises.get('directory')}/{get_jwt_identity()}/"
        return send_from_directory(path, "index.html")
    except Exception as e:
        logger.exception(f"Loading exercises from {cfg.exercises.get('directory')} failed")
        abort(e.code)


@bp.route("/exercises/<path:path>", methods=["GET"])
@jwt_required()
def serve_exercises(path):
    full_path = f"{path}index.html" if path.endswith("/") else path
    try:
        path = f"{path}index.html" if path.endswith("/") else path
        full_path = f"{get_jwt_identity()}/{path}"
        return send_from_directory(cfg.exercises.get("directory"), full_path)
    except Exception as e:
        logger.exception(f"Loading exercises from {cfg.exercises.get('directory')} failed")
        abort(e.code)


@bp.route("/admin")
@admin_required()
def admin_area():

    executions = []

    user_list = [{"id": 0, "username": "all"}]
    users = User.query.all()

    for user in users:

        user_list.append({"id": user.id, "username": user.username})
        execution = {"user_id": user.id, "username": user.username}

        for exercise in exercises[1:]:
            exercise_name = exercise["id"]
            exercise_type = exercise["type"]
            execution[exercise_name] = -1

            if exercise_type == "form":
                for exec in user.formExercises:
                    if exec.name == exercise_name:
                        execution[exercise_name] = 1

            elif exercise_type == "script":
                for exec in user.scriptExercises:
                    if exec.script_name == exercise["script"]:
                        execution[exercise_name] = exec.completed

        executions.append(execution)

    columns = [{"name": "id", "id": "user_id"}, {"name": "user", "id": "username"}]
    columns.extend({"name": exercise["name"], "id": exercise["id"]} for exercise in exercises[1:])

    return render_template("results.html", exercises=exercises, users=user_list, table={"columns": columns, "data": executions})


@bp.route("/results/<user_id>/<exercise_id>")
@admin_required()
def get_exercise_results(user_id, exercise_id):

    exercise = next(exercise for exercise in exercises if exercise["id"] == exercise_id)
    exercise_type = exercise["type"]
    data = None

    try:
        username = User.query.filter_by(id=user_id).first().username
    except:
        logger.warn("User not found.")

    try:
        if exercise_type == "form":
            data = json.loads(FormExercise.query.filter_by(user_id=user_id).filter_by(name=exercise["id"]).first().data)
        elif exercise_type == "script":
            executed, completed, history = get_history_from_DB(exercise["script"], username)
            data = {"executed": executed, "completed": completed, "history": history}
        else:
            return jsonify(error="Exercise type unknown.")
    except:
        logger.warn("No data found.")

    return render_template("results_details.html", user=username, exercise=exercise["name"], data=data)

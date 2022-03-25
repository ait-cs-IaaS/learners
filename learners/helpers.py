from flask import jsonify
from flask_mail import Message

import time
from datetime import datetime
import os
import pathlib
import json
import requests

from learners.database import Execution, Exercise, User, ScriptExercise, FormExercise
from learners.conf.config import cfg
from learners.database import db
from learners.logger import logger
from learners.mail_manager import mail


def utc_to_local(utc_datetime, date=True):
    if utc_datetime is None:
        return None
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return (utc_datetime + offset).strftime("%m/%d/%Y, %H:%M:%S") if date else (utc_datetime + offset).strftime("%H:%M:%S")


def get_history_from_DB(script_name, username):
    db_entries = (
        db.session.query(ScriptExercise)
        .filter_by(script_name=script_name)
        .join(User)
        .filter_by(username=username)
        .order_by(ScriptExercise.start_time.desc())
        .limit(10)
        .all()
    )

    history = {
        str(i + 1): {
            "start_time": utc_to_local(db_entry.start_time, date=True),
            "response_time": utc_to_local(db_entry.response_time, date=False),
            "completed": db_entry.completed,
        }
        for i, db_entry in enumerate(db_entries)
    }

    executed = bool(db_entries[0]) if (db_entries and db_entries[0].response_time) else False
    completed = db_entries[0].completed if db_entries else False

    return executed, completed, history


def check_password(usermap, user, password):
    return user in usermap and usermap.get(user).get("password") == password


def is_admin(user):
    return cfg.users.get(user).get("is_admin")


def connection_failed(execution_uuid):
    try:
        db_entry = Execution.query.filter_by(uuid=execution_uuid).first()
        db_entry.msg = "Connection failed."
        db_entry.connection_failed = True
        db.session.commit()
    except Exception as database_exception:
        logger.exception(database_exception)


def call_venjix(user, script, execution_uuid):
    try:
        response = requests.post(
            url=f"{cfg.venjix.get('url')}/{script}",
            headers=cfg.venjix.get("headers"),
            data=json.dumps(
                {
                    "script": script,
                    "user_id": user,
                    "callback": f"{cfg.callback.get('endpoint')}/{str(execution_uuid)}",
                }
            ),
        )

        state = response.json()
        executed = bool(state["response"] == "script started")
        connected = True

    except Exception as connection_exception:
        connection_failed(execution_uuid)
        logger.exception(connection_exception)
        executed = False
        connected = False

    return connected, executed


def db_create_execution(type, data, user, execution_uuid):

    name = data.get("name")
    script = data.get("script")
    form_data = json.dumps(data.get("form"), indent=4, sort_keys=False)

    try:
        exercise_id = Exercise.query.filter_by(name=name).first().id
        user_id = User.query.filter_by(username=user).first().id

        execution = Execution(type=type, script=script, form_data=form_data, uuid=execution_uuid, user_id=user_id, exercise_id=exercise_id)
        db.session.add(execution)
        db.session.commit()
        return True

    except Exception as e:
        logger.exception(e)
        return False


def send_form_via_mail(user, data):

    exercise_name = Exercise.query.filter_by(name=data.get("name")).first().pretty_name

    subject = f"Form Submission: {user} - {exercise_name}"

    mailbody = (
        "<h1>Results</h1> <h2>Information:</h2>"
        + f"<strong>User:</strong> {user}</br>"
        + f"<strong>Form:</strong> {exercise_name}</br>"
        + "<h2>Data:</h2>"
    )

    data = ""
    for (key, value) in json.dumps(data.get("form"), indent=4, sort_keys=False).items():
        value = value or "<i>-- emtpy --</i>"
        data += f"<strong>{key}</strong>: {value}</br>"

    mailbody += f"<p>{data}</p></br>"

    try:
        msg = Message(subject, sender=("Venjix", cfg.mail_sender), recipients=cfg.mail_recipients)
        msg.html = mailbody

        mail.send(msg)
        return True

    except Exception as e:
        logger.exception(e)
        return False

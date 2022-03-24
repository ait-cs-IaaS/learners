from flask import jsonify

import time
from datetime import datetime
import os
import pathlib
import json
import requests
from bs4 import BeautifulSoup

from learners.database import User, ScriptExercise, FormExercise
from learners.conf.config import cfg
from learners.database import db
from learners.logger import logger


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


def get_exercises():
    exercises = [{"id": "all", "type": "all", "exerciseWeight": 0, "parentWeight": "0", "name": "all"}]

    if cfg.exercises.get("directory").startswith("/"):
        root_directory = f"{cfg.exercises.get('directory')}/{list(cfg.users.keys())[0]}/en/"
    else:
        root_directory = f"./learners/{cfg.exercises.get('directory')}/{list(cfg.users.keys())[0]}/en/"

    for path, subdirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".html"):
                f = open(pathlib.PurePath(path, file), "r")
                parsed_html = BeautifulSoup(f.read(), features="html.parser")
                exerciseInfos = parsed_html.body.find_all("input", attrs={"class": "exercise-info"})
                exercises.extend(json.loads(exerciseInfo.get("value")) for exerciseInfo in exerciseInfos)

    for exercise in exercises:
        exerciseWeight = int(exercise["exerciseWeight"])
        parentWeight = int(exercise["parentWeight"])

        if parentWeight == 0:
            exercise["exerciseWeight"] = exerciseWeight * 10
        else:
            exercise["exerciseWeight"] = parentWeight * 10 + exerciseWeight

        exercise["name"] = exercise["id"].replace("_", " ")

    exercises = sorted(exercises, key=lambda d: d["exerciseWeight"])
    return exercises


def connection_failed(call_uuid):
    try:
        db_entry = ScriptExercise.query.filter_by(call_uuid=call_uuid).first()
        db_entry.msg = "Connection failed."
        db_entry.connection_failed = True
        db.session.commit()
    except Exception as database_exception:
        logger.exception(database_exception)


def call_venjix(user, script, call_uuid):
    try:
        response = requests.post(
            url=f"{cfg.venjix.get('url')}/{script}",
            headers=cfg.venjix.get("headers"),
            data=jsonify(
                script=script,
                user_id=user,
                callback=f"{cfg.callback.get('endpoint')}/{str(call_uuid)}",
            ),
        )

        state = response.json()
        executed = bool(state.get("response") == "script started")

        return jsonify(connected=True, executed=executed)

    except Exception as connection_exception:
        connection_failed(call_uuid)
        logger.exception(connection_exception)

        return jsonify(connected=False, executed=False)

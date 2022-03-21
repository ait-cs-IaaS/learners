import time
from datetime import datetime

import os
import pathlib
import json
from bs4 import BeautifulSoup

from learners.database import User, ScriptExercise, FormExercise
from learners.conf.config import cfg
from learners.database import db


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
        .order_by(ScriptExercise.response_time.desc())
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

    executed = bool(db_entries[0]) if db_entries else False
    completed = db_entries[0].completed if db_entries else False

    return executed, completed, history


def get_exercises():
    exercises = [{"id": "all", "type": "all", "exerciseWeight": 0, "parentWeight": "0", "name": "all"}]
    root_directory = "./learners/static/exercises/en/"
    for path, subdirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".html"):
                f = open(pathlib.PurePath(path, file), "r")
                html = f.read()
                parsed_html = BeautifulSoup(html, features="html.parser")
                exerciseInfos = parsed_html.body.find_all("input", attrs={"class": "exercise-info"})
                for exerciseInfo in exerciseInfos:
                    exercises.append(json.loads(exerciseInfo.get("value")))

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

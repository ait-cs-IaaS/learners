import json
import os
import pathlib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from learners.conf.config import cfg

from bs4 import BeautifulSoup

from sqlalchemy import event


"""
Set up the database

Learners keeps track of the training/exercise progress of the participants, for this
a locale database is created, which is initialized with the following function.
"""

db = SQLAlchemy()

# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    scriptExercises = db.relationship("ScriptExercise", backref="user", lazy=True)
    formExercises = db.relationship("FormExercise", backref="user", lazy=True)
    executions = db.relationship("Execution", backref="user", lazy=True)


class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)
    script = db.Column(db.String(120), nullable=True)
    execution_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_timestamp = db.Column(db.DateTime, nullable=True)
    response_content = db.Column(db.Text, nullable=True)
    form_data = db.Column(db.String(), nullable=True)
    msg = db.Column(db.String(240), nullable=True)
    uuid = db.Column(db.String(120), unique=True, nullable=True)
    completed = db.Column(db.Integer, nullable=False, default=0)
    connection_failed = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    pretty_name = db.Column(db.String(120), unique=True, nullable=False)
    weight = db.Column(db.String(120), nullable=False)
    executions = db.relationship("Execution", backref="exercise", lazy=True)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


# History of sent POSTs
class ScriptExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.String(120), nullable=False)
    call_uuid = db.Column(db.String(120), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_time = db.Column(db.DateTime, nullable=True)
    response_content = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Integer, nullable=False, default=0)
    connection_failed = db.Column(db.Integer, nullable=False, default=0)
    msg = db.Column(db.String(240), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# Formdata
class FormExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    data = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@event.listens_for(User.__table__, "after_create")
def insert_initial_users(*args, **kwargs):
    for user, _ in cfg.users.items():
        db.session.add(User(username=user))
    db.session.commit()


@event.listens_for(Exercise.__table__, "after_create")
def insert_exercises(*args, **kwargs):

    exercises = get_exercises()

    for exercise in exercises[1:]:
        print(exercise)
        db.session.add(
            Exercise(
                type=exercise["type"],
                name=exercise["id"],
                pretty_name=exercise["name"],
                weight=exercise["exerciseWeight"],
            )
        )
    db.session.commit()


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


def build_db(app):
    global db
    db.init_app(app)

    db.create_all()

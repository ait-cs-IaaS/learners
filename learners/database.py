# sourcery skip: avoid-builtin-shadow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, func

from learners.conf.config import cfg
from learners.functions.helpers import get_exercises

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
    executions = db.relationship("Execution", backref="user", lazy=True)


class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=False)
    script = db.Column(db.String(120), nullable=True)
    execution_timestamp = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
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


def build_db(app):
    global db
    db.init_app(app)
    db.create_all()

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from learners.conf.config import cfg

from sqlalchemy import event


"""
Set up the database

Learners keeps track of the training/exercise progress of the participants, for this
a locale database is created, which is initialized with the following function.
"""

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


# History of sent POSTs
class ScriptExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.String(120), nullable=False)
    call_uuid = db.Column(db.String(120), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_time = db.Column(db.DateTime, nullable=True)
    response_content = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Integer, nullable=False, default=0)
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


def build_db(app):
    global db
    db.init_app(app)

    db.create_all()

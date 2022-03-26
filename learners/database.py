from flask_sqlalchemy import SQLAlchemy

"""
Set up the database

Learners keeps track of the training/exercise progress of the participants, for this
a locale database is created, which is initialized with the following function.
"""

db = SQLAlchemy()


def build_db(app):
    global db

    from learners.conf.db_models import Execution, Exercise, TokenBlocklist, User
    from learners.functions.database import insert_exercises, insert_initial_users

    db.init_app(app)
    db.create_all()

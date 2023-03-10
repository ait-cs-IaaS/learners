from flask_sqlalchemy import SQLAlchemy

from backend.logger import logger


db = SQLAlchemy()


def build_db(app):
    global db

    from backend.conf.db_models import Execution, Exercise, TokenBlocklist, User
    from backend.functions.database import insert_exercises, insert_initial_users, insert_questionaires, insert_initial_usergroups

    db.init_app(app)
    db.create_all()

    insert_initial_users()
    insert_initial_usergroups()
    insert_exercises(app)
    insert_questionaires(app)

    try:
        loaded_exercises = db.session.query(Exercise).all()
        logger.info(f"\n\tCurrently, {len(loaded_exercises)} Exercises has been loaded.\n")
    except Exception as e:
        logger.exception(e)
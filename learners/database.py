from flask_sqlalchemy import SQLAlchemy

from learners.logger import logger


db = SQLAlchemy()


def build_db(app):
    global db

    from learners.conf.db_models import Execution, Exercise, TokenBlocklist, User
    from learners.functions.database import insert_exercises, insert_initial_users, insert_questionaires

    db.init_app(app)
    db.create_all()

    insert_initial_users()
    insert_exercises(app)
    insert_questionaires(app)

    try:
        loaded_exercises = db.session.query(Exercise).all()
        logger.info(f"\n\tCurrently, {len(loaded_exercises)} Exercises has been loaded.\n")
    except Exception as e:
        logger.exception(e)

from flask_sqlalchemy import SQLAlchemy

from backend.logger import logger


db = SQLAlchemy()


def build_db(app):
    global db

    from backend.conf.db_models import Exercise
    from backend.functions.database import (
        db_insert_exercises,
        db_insert_initial_users,
        db_insert_questionaires,
        db_insert_initial_usergroups,
        db_insert_pages,
    )

    db.init_app(app)
    db.create_all()

    db_insert_initial_users()
    db_insert_initial_usergroups()
    db_insert_pages(app)
    db_insert_exercises(app)
    db_insert_questionaires(app)

    try:
        loaded_exercises = db.session.query(Exercise).all()
        logger.info(f"\n\tCurrently, {len(loaded_exercises)} Exercises has been loaded.\n")
    except Exception as e:
        logger.exception(e)

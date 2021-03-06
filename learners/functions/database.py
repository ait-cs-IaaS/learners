import hashlib
import json
from datetime import datetime, timezone
from sqlite3 import IntegrityError
from typing import Tuple

from learners import logger
from learners.conf.config import cfg
from learners.conf.db_models import Attachment, Execution, Exercise, User
from learners.database import db
from learners.functions.helpers import extract_exercises
from sqlalchemy import event, nullsfirst


def insert_initial_users(*args, **kwargs):
    for user, _ in cfg.users.items():
        db.session.add(User(name=user))
    try:
        db.session.commit()
    except Exception:
        logger.debug("User data already initialized. Delete table to reinitialize.")


def insert_exercises(*args, **kwargs):
    exercises = extract_exercises()
    for exercise in exercises[1:]:
        db.session.add(
            Exercise(
                type=exercise["type"],
                name=exercise["id"],
                title=exercise["title"],
                page_title=exercise["pageTitle"],
                parent=exercise["parent"],
                weight=exercise["exerciseWeight"],
            )
        )
    try:
        db.session.commit()

    except Exception:
        logger.debug("Exercises already initialized. Delete table to reinitialize.")


def db_update_execution(
    execution_uuid: str, connection_failed=None, response_timestamp=None, response_content=None, completed=None, msg=None, partial=None
) -> None:
    try:
        execution = Execution.query.filter_by(uuid=execution_uuid).first()
        for key, value in list(locals().items())[:-1]:
            if value:
                setattr(execution, key, value)
        db.session.commit()

    except Exception as e:
        logger.exception(e)


def db_create_execution(type: str, data: dict, username: str, execution_uuid: str) -> bool:

    name = data.get("name")
    script = data.get("script")
    form_data = json.dumps(data.get("form"), indent=4, sort_keys=False)

    try:
        exercise_id = Exercise.query.filter_by(name=name).first().id
        user_id = User.query.filter_by(name=username).first().id

        execution = Execution(
            type=type,
            script=script,
            form_data=form_data,
            uuid=execution_uuid,
            user_id=user_id,
            exercise_id=exercise_id,
        )

        if type == "form":
            execution.completed = True
            execution.response_timestamp = datetime.now(timezone.utc)

        db.session.add(execution)
        db.session.commit()
        return True

    except Exception as e:
        logger.exception(e)
        return False


def get_current_executions(user_id: int, exercise_id: int) -> Tuple[dict, dict]:
    try:
        executions = db.session.query(Execution).filter_by(user_id=user_id).filter_by(exercise_id=exercise_id)
        last_execution = executions.order_by(nullsfirst(Execution.response_timestamp.desc()), Execution.execution_timestamp.desc()).first()
        executions = executions.order_by(Execution.execution_timestamp.desc()).all()
        return last_execution, executions
    except Execution as e:
        logger.exception(e)
        return None, None


def get_exercise_by_name(name: str) -> dict:
    return generic_getter(Exercise, name=name)


def get_exercise_by_id(id: int) -> dict:
    return generic_getter(Exercise, id=id)


def get_user_by_name(name: str) -> dict:
    return generic_getter(User, name=name)


def get_user_by_id(id: int) -> dict:
    return generic_getter(User, id=id)


def get_all_users() -> list:
    return generic_getter(User, all=True)


def get_all_exercises() -> list:
    return generic_getter(Exercise, all=True)


def get_exercise_groups() -> list:
    try:
        session = db.session.query(Exercise.parent).group_by(Exercise.parent).all()
        return [groupname for groupname, in session]
    except Exception as e:
        logger.exception(e)
        return None


def get_exercises_by_group(parent: str) -> list:
    try:
        session = db.session.query(Exercise).filter_by(parent=parent)
        return session.all()
    except Exception as e:
        logger.exception(e)
        return None


def generic_getter(db_model, id: int = None, name: str = None, all: bool = False) -> dict:
    try:
        session = db.session.query(db_model)
        if id:
            session = session.filter_by(id=id)
        if name:
            session = session.filter_by(name=name)
        return session.all() if all else session.first()
    except Exception as e:
        logger.exception(e)
        return None


def get_executions_by_user_exercise(user_id: int, exercise_id: int) -> list:
    try:
        return (
            db.session.query(Execution)
            .filter_by(user_id=user_id)
            .filter_by(exercise_id=exercise_id)
            .order_by(Execution.execution_timestamp.desc())
            .all()
        )
    except Exception as e:
        logger.exception(e)
        return None


def get_completed_state(user_id: int, exercise_id: int) -> dict:
    try:
        return (
            db.session.query(User)
            .filter_by(id=user_id)
            .join(Execution)
            .filter_by(exercise_id=exercise_id)
            .with_entities(Execution.completed)
            .all()
        )
    except Exception as e:
        logger.exception(e)
        return None


def db_create_file(filename: str, username: str) -> str:
    try:
        user_id = User.query.filter_by(name=username).first().id
        filename_hash = hashlib.md5(filename.encode("utf-8")).hexdigest()
        file = Attachment(filename=filename, filename_hash=filename_hash, user_id=user_id)
        db.session.add(file)
        db.session.commit()
        return filename_hash

    except Exception as e:
        logger.exception(e)
        return None


def get_filename_from_hash(filename_hash):
    try:
        session = db.session.query(Attachment).filter_by(filename_hash=filename_hash).first()
        return session.filename
    except Exception as e:
        logger.exception(e)
        return None

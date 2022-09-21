import hashlib
import json
from datetime import datetime, timezone
from sqlite3 import IntegrityError
import string
from typing import Tuple

from learners.logger import logger, EXERCISE_INFO
from learners.conf.config import cfg
from learners.conf.db_models import Attachment, Execution, Exercise, User, Comment, Questionaire, QuestionaireQuestion, QuestionaireAnswer
from learners.database import db
from learners.functions.helpers import extract_json_content
from sqlalchemy import event, nullsfirst
from sqlalchemy.orm import joinedload

from flask import escape, jsonify


def insert_initial_users(*args, **kwargs):
    for user_name, userDetails in cfg.users.items():
        user = {"name": user_name, "role": userDetails.get("role")}
        db_create_or_update(User, "name", user)


def insert_exercises(app, *args, **kwargs):
    exercises = extract_json_content(app, cfg.exercise_json, EXERCISE_INFO)
    for exercise in exercises:
        db_create_or_update(Exercise, "global_exercise_id", exercise)


def insert_questionaires(app, *args, **kwargs):
    questionaires = extract_json_content(app, cfg.questionaire_json)
    for questionaire in questionaires:
        db_create_or_update(Questionaire, "global_questionaire_id", questionaire)

    questions = extract_json_content(app, cfg.questionaires_questions_json)
    for question in questions:
        db_create_or_update(QuestionaireQuestion, "global_question_id", question)


def db_create_or_update(db_model, filter_keys: str = None, passed_element: dict = None) -> bool:
    # check if element already exists
    try:
        session = db.session.query(db_model)
        for filter_key in filter_keys.split("+"):
            kwargs = {filter_key.strip(): passed_element[filter_key.strip()]}
            session = session.filter_by(**kwargs)
        current_db_entry = session.first()
    except Exception as e:
        logger.exception(e)
        return False

    if current_db_entry:
        # Update existing
        for key in passed_element:
            if getattr(current_db_entry, key) != passed_element[key]:
                setattr(current_db_entry, key, passed_element[key])
                db.session.flush()
                logger.info(f"Updated: {key}")
    else:
        # Create new
        new_element = db_model()
        for key in passed_element:
            setattr(new_element, key, passed_element[key])
        db.session.add(new_element)
    try:
        db.session.commit()
    except Exception as e:
        logger.exception(e)
        return False
    return True


def db_update_execution(
    execution_uuid: str, connection_failed=None, response_timestamp=None, response_content=None, completed=None, msg=None, partial=None
) -> None:
    try:
        execution = Execution.query.filter_by(execution_uuid=execution_uuid).first()
        for key, value in list(locals().items())[:-1]:
            if value:
                setattr(execution, key, value)
        db.session.commit()

    except Exception as e:
        logger.exception(e)


def db_create_execution(exercise_type: str, data: dict, username: str, execution_uuid: str) -> bool:

    global_exercise_id = data.get("name")
    script = data.get("script")
    form_data = json.dumps(data.get("form"), indent=4, sort_keys=False)

    try:
        exercise_id = Exercise.query.filter_by(global_exercise_id=global_exercise_id).first().id
        user_id = User.query.filter_by(name=username).first().id

        execution = Execution(
            exercise_type=exercise_type,
            script=script,
            form_data=form_data,
            execution_uuid=execution_uuid,
            user_id=user_id,
            exercise_id=exercise_id,
        )

        if exercise_type == "form":
            execution.completed = True
            execution.response_timestamp = datetime.now(timezone.utc)

        db.session.add(execution)
        db.session.commit()
        return True

    except Exception as e:
        logger.exception(e)
        return False


def db_create_questionaire_execution(global_questionaire_id: str, answers: dict, username: str) -> bool:

    try:
        user = get_user_by_name(username)
        if user.role != "participant":
            return False

        for global_question_id, answer in answers.items():
            new_answer = {
                "user_id": user.id,
                "answer": answer,
                "global_question_id": global_question_id,
                "global_questionaire_id": global_questionaire_id,
            }
            db_create_or_update(QuestionaireAnswer, "user_id + global_question_id", new_answer)
        return True

    except Exception as e:
        logger.exception(e)
        return False


def db_create_comment(data: dict, username: str) -> bool:

    try:
        comment = Comment(
            comment=escape(data.get("comment")),
            user_id=User.query.filter_by(name=username).first().id,
            global_exercise_id=data.get("global_exercise_id"),
        )

        db.session.add(comment)
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


def get_exercise_by_name(exercise_name: str) -> dict:
    return generic_getter(Exercise, "exercise_name", exercise_name)


def get_exercise_by_global_exercise_id(global_exercise_id: str) -> dict:
    return generic_getter(Exercise, "global_exercise_id", global_exercise_id)


def get_questionaire_by_global_questionaire_id(global_questionaire_id: str) -> dict:
    return generic_getter(Questionaire, "global_questionaire_id", global_questionaire_id)


def get_all_questionaires_questions(global_questionaire_id: str) -> dict:
    try:
        return (
            db.session.query(QuestionaireQuestion)
            .filter_by(global_questionaire_id=global_questionaire_id)
            .order_by(QuestionaireQuestion.local_question_id.asc())
            .all()
        )
    except Exception as e:
        logger.exception(e)
        return None


def get_exercise_by_id(id: int) -> dict:
    return generic_getter(Exercise, "id", id)


def get_user_by_name(name: str) -> dict:
    return generic_getter(User, "name", name)


def get_user_by_id(id: int) -> dict:
    return generic_getter(User, "id", id)


def get_all_users() -> list:
    return generic_getter(User, "role", "participant", all=True)


def get_all_exercises() -> list:
    return generic_getter(Exercise, all=True)


def get_all_comments() -> list:
    return generic_getter(Comment, all=True)


def get_exercise_groups() -> list:
    try:
        session = db.session.query(Exercise.parent_page_title).group_by(Exercise.parent_page_title).all()
        return [groupname for groupname, in session]
    except Exception as e:
        logger.exception(e)
        return None


def get_exercises_by_group(parent_page_title: str) -> list:
    try:
        session = db.session.query(Exercise).filter_by(parent_page_title=parent_page_title)
        return session.all()
    except Exception as e:
        logger.exception(e)
        return None


def generic_getter(db_model, filter_key: str = None, filter_value: str = None, all: bool = False) -> dict:
    try:
        session = db.session.query(db_model)
        if filter_key and filter_value:
            kwargs = {filter_key: filter_value}
            session = session.filter_by(**kwargs)
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
        return db.session.query(Attachment).filter_by(filename_hash=filename_hash).first()
    except Exception as e:
        logger.exception(e)
        return None


def get_all_exercises_sorted() -> list:
    try:
        return db.session.query(Exercise).order_by(Exercise.order_weight.asc()).all()
    except Exception as e:
        logger.exception(e)
        return None


def get_all_questionaires_sorted() -> list:
    try:
        return db.session.query(Questionaire).order_by(Questionaire.order_weight.asc()).all()
    except Exception as e:
        logger.exception(e)
        return None


def get_completion_percentage(exercise_id):

    users = get_all_users()

    try:
        executions = (
            db.session.query(Execution)
            .filter_by(exercise_id=exercise_id)
            .join(User)
            .group_by(User.id)
            .with_entities(db.func.max(Execution.completed))
            .all()
        )
        return len(executions) / len(users) * 100

    except Exception as e:
        logger.exception(e)
        return 0


def get_questionaire_completion_percentage(global_questionaire_id):

    users = get_all_users()

    try:
        answers = (
            db.session.query(QuestionaireAnswer).filter_by(global_questionaire_id=global_questionaire_id).join(User).group_by(User.id).all()
        )
        return len(answers) / len(users) * 100

    except Exception as e:
        logger.exception(e)
        return 0


def get_results_of_single_exercise(global_exercise_id):
    try:
        return (
            db.session.query(Execution)
            .join(Exercise)
            .filter_by(global_exercise_id=global_exercise_id)
            .join(User)
            .order_by(Execution.completed.desc(), Execution.execution_timestamp.desc())
            .group_by(User.id)
            .with_entities(
                User.name, Execution.id, Execution.user_id, Execution.execution_timestamp, Execution.completed, Exercise.global_exercise_id
            )
            .all()
        )

    except Exception as e:
        logger.exception(e)
        return 0


def get_question_counts(global_question_id):
    try:
        options = db.session.query(QuestionaireQuestion).filter_by(global_question_id=global_question_id).first().options
        labels = [option.strip() for option in (options).split(";")]
        counts = []

        for label in labels:
            counts.append(
                db.session.query(QuestionaireAnswer).filter_by(answer=label).filter_by(global_question_id=global_question_id).count()
            )

        prepended_labels = [f"{alpha}. {label}" for (label, alpha) in zip(labels, list(string.ascii_uppercase))]

        return prepended_labels, counts

    except Exception as e:
        logger.exception(e)
        return [""], [0]

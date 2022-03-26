import json
from datetime import datetime, timezone
from typing import Tuple

from learners import logger
from learners.database import Execution, Exercise, User, db
from sqlalchemy import nullsfirst


def db_update_execution(
    execution_uuid: str, connection_failed=None, response_timestamp=None, response_content=None, completed=None, msg=None
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
        user_id = User.query.filter_by(username=username).first().id

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

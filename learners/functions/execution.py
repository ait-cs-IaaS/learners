import json
import time
from typing import Tuple

import requests
from flask_mail import Message
from learners.logger import logger
from learners.conf.config import cfg
from learners.conf.db_models import Execution, Exercise
from learners.database import db
from learners.functions.database import db_update_execution
from learners.functions.helpers import extract_history


def call_venjix(username: str, script: str, execution_uuid: str) -> Tuple[bool, bool]:
    try:
        response = requests.post(
            url=f"{cfg.venjix.get('url')}/{script}",
            headers=cfg.venjix.get("headers"),
            data=json.dumps(
                {
                    "script": script,
                    "user_id": username,
                    "callback": f"{cfg.callback.get('endpoint')}/{execution_uuid}",
                }
            ),
        )

        resp = response.json()
        connection_failed = False
        executed = bool(resp["response"] == "script started")
        msg = resp.get("msg") or None

    except Exception as connection_exception:
        logger.exception(connection_exception)

        connection_failed = True
        executed = False
        msg = "Connection failed"

    db_update_execution(execution_uuid, connection_failed=connection_failed, msg=msg)
    return not connection_failed, executed


def wait_for_response(execution_uuid: str) -> dict:
    while True:
        time.sleep(0.5)

        try:
            execution = Execution.query.filter_by(uuid=execution_uuid).first()
            if execution.response_timestamp or execution.connection_failed:
                return execution
            db.session.close()

        except Exception as e:
            logger.exception(e)
            return None


def update_execution_response(response: dict, last_execution, executions: list) -> dict:

    if last_execution:
        response["completed"] = last_execution.completed
        response["executed"] = int(not last_execution.connection_failed)
        response["msg"] = last_execution.msg
        response["response_timestamp"] = last_execution.response_timestamp
        response["connection_failed"] = last_execution.connection_failed
        response["partial"] = last_execution.partial
        executions[0] = last_execution

    response["history"] = extract_history(executions)

    return response

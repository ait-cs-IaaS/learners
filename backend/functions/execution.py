import json
import time
from typing import Tuple

import requests
from backend.functions.helpers import convert_to_dict
from backend.logger import logger
from backend.conf.config import cfg
from backend.functions.database import (
    db_get_exercise_by_id,
    db_get_submission_by_execution_uuid,
    db_update_venjix_execution,
)


def call_venjix(exercise_id: str, username: str, callback_url: str, execution_uuid: str) -> Tuple[bool, bool]:
    script_response = None
    script = db_get_exercise_by_id(exercise_id).script_name
    try:
        response = requests.post(
            # TODO: Remove verify line
            verify=False,
            url=f"{cfg.venjix.get('url')}/{script}",
            headers=cfg.venjix.get("headers"),
            data=json.dumps(
                {
                    "script": script,
                    "user_id": username,
                    "callback": f"{callback_url}/{execution_uuid}",
                }
            ),
        )

        resp = response.json()
        if response.status_code != 200:
            connected = False
            executed = False
            status_msg = f"{response.status_code}: {resp['response']}"
        else:
            connected = True
            executed = bool(resp["response"] == "script started")
            status_msg = resp.get("status_msg") or None
            script_response = resp.get("script_response") or None

    except Exception as connection_exception:
        logger.error(connection_exception)
        connected = False
        executed = False
        status_msg = "connection failed"

    updates = {
        "execution_uuid": execution_uuid,
        "executed": executed,
        "status_msg": status_msg,
        "script_response": script_response,
    }

    db_update_venjix_execution(updates)

    return connected, executed


def wait_for_venjix_response(execution_uuid: str) -> dict:
    while True:
        time.sleep(0.5)

        try:
            submission = db_get_submission_by_execution_uuid(execution_uuid)
            submission = convert_to_dict(submission)
            if not submission["executed"]:
                submission["status_msg"] = (
                    submission["status_msg"] or json.loads(submission["response_content"]).get("stderr") or "connection failed"
                )
                return submission

            if submission["response_timestamp"]:
                return submission

        except Exception as e:
            logger.exception(e)
            return None

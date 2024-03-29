import json
import os
import time
from datetime import datetime
from backend.logger import logger

from backend.conf.config import cfg


def utc_to_local(utc_datetime: str, date: bool = True) -> str:
    if utc_datetime is None:
        return None
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return (utc_datetime + offset).strftime("%m/%d/%Y, %H:%M:%S") if date else (utc_datetime + offset).strftime("%H:%M:%S")


def extract_json_content(app, json_file_path, info="") -> list:
    gen_list = []

    if (json_file_path).startswith("/"):
        json_file = json_file_path
    else:
        json_file = os.path.join(app.root_path, json_file_path)

    try:
        with open(json_file, "r") as input_file:
            json_data = json.load(input_file)
            gen_list.extend(element for _, element in json_data.items())

    except Exception:
        err = f"\n\tERROR: Could not read JSON file: {json_file}.\n{info}"
        logger.warning(err)

    return gen_list


def extract_history(executions):
    return {
        str(i + 1): {
            "start_time": utc_to_local(execution.get("execution_timestamp"), date=True),
            "response_time": utc_to_local(execution.get("response_timestamp"), date=False),
            "completed": bool(execution.get("completed")),
            "msg": execution.get("msg"),
            "partial": bool(execution.get("partial")),
        }
        for i, execution in enumerate(executions)
    }


def append_key_to_dict(dictobj: dict, parent: str, baseobj: dict = None) -> dict:
    if not dictobj.get(parent):
        dictobj[parent] = baseobj or {}
    return dictobj


def append_or_update_subexercise(parent_exercise: dict, child_exercise: dict) -> dict:
    parent_exercise["total"] += child_exercise.get("total")
    parent_exercise["done"] += child_exercise.get("done")

    for i, element in enumerate(parent_exercise.get("exercises")):
        if element.get("title") == child_exercise.get("title"):
            parent_exercise["exercises"][i]["total"] += child_exercise.get("total")
            parent_exercise["exercises"][i]["done"] += child_exercise.get("done")
            return parent_exercise

    parent_exercise["exercises"].append(child_exercise)

    return parent_exercise


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in cfg.allowed_extensions


def replace_attachhment_with_url(formData):
    if formData:
        from backend.functions.database import db_get_filename_from_hash

        for key, value in formData.items():
            if key == "attachment":
                filename = db_get_filename_from_hash(value)
                hyperlink = f"/upload/{filename}"
                formData[key] = hyperlink
            if isinstance(value, dict):
                formData[key] = replace_attachhment_with_url(value)
                continue

    return formData


def sse_create_and_publish(event: str = "newNotification", message: str = "", user=None, page=None, exercise=None) -> bool:
    # Import
    from backend.classes.SSE import SSE_Event, sse
    from backend.functions.database import db_create_notification, db_get_admin_users

    # Conditional publishing
    if event == "newSubmission":
        message = f"<h4>New submission</h4>User: {user.name}<br>Exercise: {exercise.exercise_name}"
        recipients = [admin_user.id for admin_user in db_get_admin_users()]

    if event == "newComment":
        message = f"<h4>New Comment</h4>User: {user.name}<br>Page: {page}"
        recipients = [admin_user.id for admin_user in db_get_admin_users()]

    new_event = SSE_Event(
        event=event,
        message=message,
        recipients=recipients,
    )

    # Create Database entry
    db_create_notification(new_event)

    # Notify Users
    sse.publish(new_event)


def is_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False


# remove instance element from db result
def convert_to_dict(input):
    if single := not isinstance(input, list):
        input = [input]

    output = []
    for element in input:
        element = element.__dict__
        element.pop("_sa_instance_state")
        output.append(element)

    return output[0] if single else output

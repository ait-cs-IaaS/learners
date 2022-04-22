import json
import os
import pathlib
import time
from datetime import datetime

from bs4 import BeautifulSoup
from learners.conf.config import cfg


def utc_to_local(utc_datetime: str, date: bool = True) -> str:
    if utc_datetime is None:
        return None
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return (utc_datetime + offset).strftime("%m/%d/%Y, %H:%M:%S") if date else (utc_datetime + offset).strftime("%H:%M:%S")


def extract_exercises() -> list:
    exercises = [{"id": "all", "type": "all", "exerciseWeight": 0, "parentWeight": "0", "name": "all", "parent": None}]

    if cfg.exercises.get("directory").startswith("/"):
        root_directory = f"{cfg.exercises.get('directory')}/{list(cfg.users.keys())[0]}/en/"
    else:
        root_directory = f"./learners/{cfg.exercises.get('directory')}/{list(cfg.users.keys())[0]}/en/"

    for path, subdirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".html"):
                f = open(pathlib.PurePath(path, file), "r")
                parsed_html = BeautifulSoup(f.read(), features="html.parser")
                exerciseInfos = parsed_html.body.find_all("input", attrs={"class": "exercise-info"})
                for exerciseInfo in exerciseInfos:
                    exerciseDict = json.loads(exerciseInfo.get("value"))
                    exercises.append(exerciseDict)

    for exercise in exercises:
        exerciseWeight = int(exercise["exerciseWeight"])
        parentWeight = int(exercise["parentWeight"])
        exercise["exerciseWeight"] = exerciseWeight * 10 if (parentWeight == 0) else parentWeight * 10 + exerciseWeight
        exercise["name"] = exercise["id"]
        if exercise["parent"] == "Exercises":
            exercise["parent"] = None

    exercises = sorted(exercises, key=lambda d: d["exerciseWeight"])
    return exercises


def extract_history(executions):
    return {
        str(i + 1): {
            "start_time": utc_to_local(execution.execution_timestamp, date=True),
            "response_time": utc_to_local(execution.response_timestamp, date=False),
            "completed": bool(execution.completed),
            "msg": execution.msg,
            "partial": bool(execution.partial),
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

    for (i, element) in enumerate(parent_exercise.get("exercises")):
        if element.get("title") == child_exercise.get("title"):
            parent_exercise["exercises"][i]["total"] += child_exercise.get("total")
            parent_exercise["exercises"][i]["done"] += child_exercise.get("done")
            return parent_exercise

    parent_exercise["exercises"].append(child_exercise)

    return parent_exercise


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in cfg.allowed_extensions


def replace_attachhment_with_url(formData):
    from learners.functions.database import get_filename_from_hash

    for key, value in formData.items():
        if key == "attachment":
            filename = get_filename_from_hash(value)
            hyperlink = f"/upload/{filename}"
            formData[key] = hyperlink
        if isinstance(value, dict):
            formData[key] = replace_attachhment_with_url(value)
            continue

    return formData

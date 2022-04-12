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


def get_index_of_existing_element(list_obj: list, key: str, subkey: str, elementkey: str, elementvalue: str) -> int:
    try:
        for (index, element) in enumerate(list_obj[key].get(subkey)):
            if element[elementkey] == elementvalue:
                return index
    except:
        return None
    return None

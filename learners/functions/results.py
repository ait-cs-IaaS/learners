from typing import Tuple

from learners.functions.database import get_all_exercises, get_all_users, get_completed_state
from learners.logger import logger


def construct_results_table(exercises, users) -> Tuple[dict, dict]:

    try:
        exercises = get_all_exercises()
        users = get_all_users()

        rows = []
        for user in users:
            row = {"user_id": user.id, "username": user.name}
            for exercise in exercises:
                completed_state = [state[0] for state in get_completed_state(user.id, exercise.id)]
                row[exercise.exercise_name] = int(any(completed_state)) if completed_state else -1
            rows.append(row)

        columns = [{"col_name": "id", "col_id": "user_id"}, {"col_name": "user", "col_id": "username"}]
        columns.extend({"col_id": exercise.exercise_name, "col_name": exercise.page_title} for exercise in exercises)

        return {"columns": columns, "rows": rows}

    except Exception as e:
        logger.exception(e)
        return None

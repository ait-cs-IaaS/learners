from typing import Tuple

from learners.functions.database import get_completed_state
from learners.logger import logger


def construct_results_table(exercises, users) -> Tuple[dict, dict]:

    try:
        rows = []
        for user in users:
            row = {"user_id": user.id, "username": user.name}
            for exercise in exercises:
                completed_state = [state[0] for state in get_completed_state(user.id, exercise.id)]
                row[exercise.global_exercise_id] = int(any(completed_state)) if completed_state else -1
            rows.append(row)

        columns = [{"col_id": "username", "col_name": "user"}]
        columns.extend({"col_id": exercise.global_exercise_id, "col_name": exercise.exercise_name} for exercise in exercises)

        return {"columns": columns, "rows": rows}

    except Exception as e:
        logger.exception(e)
        return None

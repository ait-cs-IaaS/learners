from typing import Tuple

from learners_backend.functions.database import get_completed_state
from learners_backend.logger import logger


def construct_results_table(exercises, users) -> Tuple[dict, dict]:

    try:
        rows = []
        for user in users:
            row = {"user_id": user.id, "username": user.name}
            for exercise in exercises:
                completed_state = [state[0] for state in get_completed_state(user.id, exercise.id)]
                row[exercise.global_exercise_id] = int(any(completed_state)) if completed_state else -1
            rows.append(row)

        cols = [{"id": "username", "name": "user"}]
        cols.extend({"id": exercise.global_exercise_id, "name": exercise.exercise_name} for exercise in exercises)

        return {"cols": cols, "rows": rows}

    except Exception as e:
        logger.exception(e)
        return None

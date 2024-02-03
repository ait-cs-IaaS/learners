import json
import string
from backend.functions.helpers import extract_history


class SubmissionResponse:
    def __init__(
        self,
        completed: bool = False,
        executed: bool = False,
        status_msg: string = "",
        response_timestamp: string = "",
        history: list = [],
        partial: bool = False,
        exercise_type: string = "",
        filename: string = "",
        uuid: string = "",
        script_response: string = "",
    ):
        self.completed = completed
        self.executed = executed
        self.status_msg = status_msg
        self.response_timestamp = response_timestamp
        self.history = history
        self.partial = partial
        self.exercise_type = exercise_type
        self.filename = filename
        self.uuid = uuid
        self.script_response = script_response

    def update(self, executions) -> dict:
        if not len(executions):
            return

        if isinstance(executions, list):
            last_execution = executions[0]
            self.history = extract_history(executions)
        else:
            last_execution = executions

        self.status_msg = last_execution.get("status_msg")
        self.response_timestamp = last_execution.get("response_timestamp")
        self.partial = last_execution.get("partial")
        self.completed = last_execution.get("completed")
        self.executed = last_execution.get("executed")
        self.exercise_type = last_execution.get("exercise_type")
        self.script_response = last_execution.get("script_response")

        if self.response_timestamp:
            if self.exercise_type == "form":
                self.executed = True
            else:
                # Get error status_msg
                error = json.loads(last_execution.get("response_content")).get("stderr")
                self.executed = bool(not error)
                # Apply error status_msg to status_msg if none given
                self.status_msg = self.status_msg or error

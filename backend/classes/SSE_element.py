import json
import string


class SSE_element:
    def __init__(
        self,
        event: string = "",
        message: string = "",
        recipients: list = [],
        positions: list = ["all"],
    ):
        self.event = event
        self.message = message
        self.positions = positions
        self.recipients = recipients

    def __repr__(self) -> str:
        return f"{type(self).__name__}(event={self.event}, message={self.message}, recipients={self.recipients}, positions={self.positions})"

    def toJson(self):
        return json.dumps({"message": self.message, "positions": self.positions})
        # if self.event == "newNotification":
        # if self.event == "newSubmission":
        #     return json.dumps({"message": self.message, "positions": ["all"]})
        # return ""

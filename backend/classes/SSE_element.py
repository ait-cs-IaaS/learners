import json
import string


class SSE_element:
    def __init__(
        self,
        event: string = "",
        message: string = "",
        recipients: list = [],
        positions: list = [],
    ):
        self.event = event
        self.message = message
        self.recipients = recipients
        self.positions = positions

    def __repr__(self) -> str:
        return f"{type(self).__name__}(message={self.message}, recipients={self.recipients}, positions={self.positions})"

    def toJson(self):
        if self.event == "newNotification":
            return json.dumps({"message": self.message, "positions": self.positions})
        return ""

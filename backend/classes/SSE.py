import queue
import json
import string


class SSE_Event:
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


class SSE_Manager:
    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=20)
        self.listeners.append(q)
        return q

    def publish(self, data: SSE_Event, event=None):
        # msg = self.format_sse(data, event)

        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(data)
            except queue.Full:
                del self.listeners[i]

    # def format_sse(self, data: str, event=None) -> str:
    #     # if isinstance(data, dict):
    #     #     data = json.dumps(data)
    #     # msg = f"data: {data}\n\n"
    #     # if event is not None:
    #     #     msg = f"event: {event}\n{msg}"
    #     return f"event: {event}\ndata:{data}\n\n"


sse = SSE_Manager()

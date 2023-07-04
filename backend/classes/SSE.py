import queue
import json
import string


class SSE_Event:
    def __init__(self, event: string = "", message: string = "", recipients: list = [], positions: list = ["all"], question: dict = {}):
        self.event = event
        self.message = message
        self.positions = positions
        self.recipients = recipients
        self.question = question

    def toJson(self):
        return json.dumps({"message": self.message, "positions": self.positions, "question": self.question})


class SSE_Manager:
    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=20)
        self.listeners.append(q)
        return q

    def publish(self, data: SSE_Event, event=None):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(data)
            except queue.Full:
                del self.listeners[i]


sse = SSE_Manager()

import queue
import json

from backend.classes.SSE_element import SSE_element


class SSE:
    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=20)
        self.listeners.append(q)
        return q

    def publish(self, data: SSE_element, event=None):
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


sse = SSE()

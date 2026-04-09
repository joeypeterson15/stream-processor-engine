import time


class GlobalClicksEventHandler:
    def init(self, window, sink_desitination):
        self.window = window
        self.sink_desitination = sink_desitination
        self.clicks = []

    def process_event(self, event):
        event_t = event["timestamp"]
        self.clicks.append(event_t)

        now_t = time.time()
        self.clicks = [t for t in self.clicks if now_t - t <= self.window]

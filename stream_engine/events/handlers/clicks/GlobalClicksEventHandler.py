import time

class GlobalClicksEventHandler:
    def __init__(self, window: float = 60.0, sink_destination: str | None = None):
        self.window = window
        self.sink_destination = sink_destination
        self.clicks = []

    def process_event(self, event_id: int, event, store, event_type: str):
        event_t = event["timestamp"]
        self.clicks.append(event_t)

        # now_t = time.time()
        # self.clicks = [t for t in self.clicks if now_t - t <= self.window]

        now_t = time.time()
        i = 0
        while i < len(self.clicks) and now_t - self.clicks[i] > self.window:
            i += 1
        if i:
            self.clicks = self.clicks[i:]

        store.write(f"{event_type}:global", self.clicks)

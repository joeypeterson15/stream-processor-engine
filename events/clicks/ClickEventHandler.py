import time


class ClickEventHandler:
    def init(self, window, sink_destination):
        self.window = window
        self.sink_desitination = sink_destination
        self.clicks = {}

    def process_event(self, event):
        event_t = event["timestamp"]
        prod_id = event["prod_id"]
        if prod_id not in self.clicks:
            self.clicks[prod_id] = []
        self.clicks[prod_id].append(event_t)

        now_t = time.time()
        self.clicks[prod_id] = [
            t for t in self.clicks[prod_id] if now_t - t <= self.window
        ]

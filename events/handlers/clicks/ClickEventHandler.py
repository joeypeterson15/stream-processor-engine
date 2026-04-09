import time


class ClickEventHandler:
    def init(self, window, sink_destination):
        self.window = window
        self.sink_desitination = sink_destination
        self.clicks = {}

    def process_event(self, event):
        # event_t = event["timestamp"]
        prod_id = event["prod_id"]
        session_id = event["session_id"]
        user_id = event["user_id"]

        if user_id not in self.clicks:
            self.clicks[user_id] = {}
        self.clicks[user_id][(prod_id, session_id)] = 1 + self.clicks[user_id].get((prod_id, session_id), 0)

        # EVICT OLDER SESSIONS PER USER
        for p, s in self.clicks[user_id]:
            if s != session_id:
                self.clicks[user_id].remove((p, s))

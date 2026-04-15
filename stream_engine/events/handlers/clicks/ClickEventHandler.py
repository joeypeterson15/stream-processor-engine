from typing import Any, Optional

class ClickEventHandler:
    def __init__(self, window: float = 60.0, sink_destination: Optional[str] = None):
        self.window = window
        self.sink_destination = sink_destination
        self.clicks = {}

    def process_event(self, event_id: int, event: Any, store, event_type: str):
        prod_id = event["prod_id"]
        session_id = event["session_id"]
        user_id = event["user_id"]

        if user_id not in self.clicks:
            self.clicks[user_id] = {}

        if session_id not in self.clicks[user_id]:
            self.clicks[user_id][session_id] = {}

        self.clicks[user_id][session_id][prod_id] = 1 + self.clicks[user_id][session_id].get(prod_id, 0)

        # EVICT OLDER SESSIONS PER USER
        for session in list(self.clicks[user_id].keys()):
            if session != session_id:
                del self.clicks[user_id][session]

        store.write(f"{event_type}:by_user", self.clicks)
    

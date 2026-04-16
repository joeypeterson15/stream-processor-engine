import time

class GlobalOrdersEventHandler:
    def __init__(self, window: float = 60.0, sink_destination: str | None = None):
        self.window = window
        self.sink_destination = sink_destination
        self.orders = []

    def process_event(self, event_id: int, event, store, event_type: str):
        event_t = event["timestamp"]
        self.orders.append(event_t)


        # EVICT OLD EVENTS
        now_t = time.time()
        i = 0
        while i < len(self.orders) and now_t - self.orders[i] > self.window:
            i += 1
        if i:
            self.orders = self.orders[i:]

        store.write(f"{event_type}:global", self.orders)

        

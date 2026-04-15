from typing import Any, Optional
import time

class OrderEventHandler:
    def __init__(self, window: float = 60.0, sink_destination: Optional[str] = None):
        self.window = window
        self.sink_destination = sink_destination
        self.orders = {}

    def process_event(self, event_id: int, event: Any, store, event_type: str):
        event_t = event["timestamp"]
        prod_id = event["prod_id"]
        if prod_id not in self.orders:
            self.orders[prod_id] = []
        self.orders[prod_id].append(event_t)

        # EVICT OLD EVENTS
        now_t = time.time()
        # Remove events older than the window for the given prod_id
        self.orders[prod_id] = [
            t for t in self.orders[prod_id] if now_t - t <= self.window
        ]

        store.write(f"{event_type}:by_product", self.orders)
          
        

        

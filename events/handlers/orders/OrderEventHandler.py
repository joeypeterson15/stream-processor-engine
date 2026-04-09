from typing import Any
import collections
import time

class OrderEventHandler():
    def init(self, window, sink_desitination):
        self.window = window
        self.sink_desitination = sink_desitination
        # self.payload_fields = ['prod_id', 'timestamp']
        self.orders = {}

    def process_event(self, event):
        event_t = event['timestamp']
        prod_id = event['prod_id']
        if prod_id not in self.orders:
            self.orders[prod_id] = []
        self.orders[prod_id].append(event_t)

        # EVICT OLD EVENTS
        now_t = time.time()
        # Remove events older than the window for the given prod_id
        self.orders[prod_id] = [
            t for t in self.orders[prod_id] if now_t - t <= self.window
        ]
          
        

        

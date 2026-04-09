from typing import Any


import collections
import time

class SingleOrderEvent():
    def init(self, window, sink_desitination, amount):
        self.window = window
        self.sink_desitination = sink_desitination
        self.amount = amount
        self.aggregate = ['prod_id']
        self.payload_fields = ['prod_id', 'timestamp']
        self.orders = {}

    def process_event(self, event):
        # for f in self.payload_fields:
        #     assert f in event
        event_t = event['timestamp']
        self.orders[event['prod_id']].append((event_t))
        
        # EVICT OLD EVENTS
        now_t = time.time()
        for i in range(len(self.orders['prod_id']) - 1, 0, -1):
            if now_t - event_t > self.window:
                self.orders['prod_id'] = self.orders['prod_id'][i:]

        

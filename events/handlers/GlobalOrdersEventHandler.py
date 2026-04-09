import time

class GlobalOrdersEventHandler():
    def init(self, window, sink_desitination):
        self.window = window
        self.sink_desitination = sink_desitination
        self.orders = []

    def process_event(self, event):
        event_t = event['timestamp']
        self.orders.append(event_t)


        # EVICT OLD EVENTS
        now_t = time.time()
        i = 0
        while now_t - event_t > self.window:
            i += 1
        self.orders = self.orders[i:]

          
        

class StateStore():
    def __init__(self):
        self.store = {}

    def write(self, event_type, data):
        self.store[event_type] = data

    def read_all(self):
        return self.store

    def read(self, event_type):
        return self[event_type]
from events.event_types import event_type_to_handlers
from events.event_types import get_event_type
import collections

class BaseHandler():
    def __init__(self, store):
        self.event_handlers = self._generate_event_handlers()
        self.store = store

    def _generate_event_handlers():
        event_handlers = {}
        for type, handlers in event_type_to_handlers.items():
            event_handlers[type] = []
            for handler in handlers:
                event_handlers[type].append(handler())

        return event_handlers

    def process(self, event_id, event):
        event_type = get_event_type(event_id)
        for handler in self.event_handlers[event_type]:
            handler.process_event(event, self.store)
            # ADD STORE PIPELINE HERE
            
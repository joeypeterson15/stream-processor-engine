from events.event_types import eventHandlers
from events.event_types import get_event_type
import collections

class BaseHandler():
    def __init__(self):
        self.event_handlers = self._generate_event_handlers()

    def _generate_event_handlers():
        event_handlers = {}
        for type, handlers in eventHandlers.items():
            event_handlers[type] = []
            for handler in handlers:
                event_handlers[type].append(handler())

        return event_handlers
        
    # def _get_event_types(self,event_id):
    #     return self.eventid_types[event_id]

    def process(self, event_id, event):
        event_type = get_event_type(event_id)
        for handler in self.event_handlers[event_type]:
            handler.process_event(event)
            
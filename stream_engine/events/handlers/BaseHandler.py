from stream_engine.events.event_types import event_type_to_handlers, get_event_type

class BaseHandler:
    def __init__(self):
        self.event_handlers = self._generate_event_handlers()

    def _generate_event_handlers(self):
        event_handlers = {}
        for event_type, handlers in event_type_to_handlers.items():
            event_handlers[event_type] = []
            for handler in handlers:
                event_handlers[event_type].append(handler())

        return event_handlers

    def process(self, event_id, event, store):
        event_type = get_event_type(event_id)
        for handler in self.event_handlers[event_type]:
            handler.process_event(event_id, event, store, event_type)
            
from events.event_types import eventHandlersList
# from events.handlers import click, global_clicks, global_orders, order
class BaseHandler():
    def __init__(self):
        self.events = eventHandlers
        self.event_handlers = self.generate_event_handlers()


    def generate_event_handlers():
        event_handlers = {}
        for eventHandler in eventHandlers:
            
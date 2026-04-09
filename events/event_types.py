from events.handlers import ClickHandler
from events.handlers.order import OrderHandler

eventHandlers = {
    "click": ClickHandler,
    "order": OrderHandler,
}

event_id_types = {
    1: { 'order': ["OrderEvent", "GlobalOrdersEvent"]},
    2: { 'click': ["ClickEvent", "GlobalClicks"]},
}

def get_event_types(event_id):
    return event_id_types[event_id]
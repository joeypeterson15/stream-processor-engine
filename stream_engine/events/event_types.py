# from events.handlers.clicks import ClickHandler
from events.handlers.orders.OrderEventHandler import OrderEventHandler
from events.handlers.orders.GlobalOrdersEventHandler import GlobalOrdersEventHandler
from events.handlers.clicks.ClickEventHandler import ClickEventHandler
from events.handlers.clicks.GlobalClicksEventHandler import GlobalClicksEventHandler

event_type_to_handlers = {
    "clicks": [ClickEventHandler, GlobalClicksEventHandler],
    "orders": [OrderEventHandler, GlobalOrdersEventHandler],
}

event_id_to_type = {
    1: "clicks",
    2: "orders"
}

def get_event_type(event_id):
    return event_id_to_type[event_id]
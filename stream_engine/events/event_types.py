from stream_engine.events.handlers.orders.OrderEventHandler import OrderEventHandler
from stream_engine.events.handlers.orders.GlobalOrdersEventHandler import GlobalOrdersEventHandler
from stream_engine.events.handlers.clicks.ClickEventHandler import ClickEventHandler
from stream_engine.events.handlers.clicks.GlobalClicksEventHandler import GlobalClicksEventHandler

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
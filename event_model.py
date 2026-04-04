# E COMMERCE DATA MODEL

event_types = {
    1: "OrderEvent",
    2: "CustomerEvent",
    3: "ProductEvent",
    4: "ClickEvent",
    5: "ViewEvent",
    6: "AddToCartEvent",
    7: "RemoveFromCartEvent",
    8: "CheckoutEvent",
    9: "PurchaseEvent",
    10: "RefundEvent",
    11: "CancelEvent",
}

class BaseEvent():
    def __init__(self, event_type, event_data, metadata):
        self.event_type = event_type
        self.event_data = event_data
        self.metadata = metadata

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "event_data": self.event_data,
            "metadata": self.metadata
        }
    
    def process_metadata(self):
        pass

class OrderEvent(BaseEvent):
    def __init__(self, event_type, event_data, metadata):
        super().__init__(event_type, event_data, metadata)
    
class CustomerEvent(BaseEvent):
    def __init__(self, event_type, event_data, metadata):
        super().__init__(event_type, event_data, metadata)

class ProductEvent(BaseEvent):
    def __init__(self, event_type, event_data, metadata):
        super().__init__(event_type, event_data, metadata)

class ClickEvent(BaseEvent):
    def __init__(self, event_type, event_data, metadata):
        super().__init__(event_type, event_data, metadata)

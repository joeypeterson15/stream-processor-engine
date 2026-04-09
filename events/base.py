class BaseEvent():

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "event_data": self.event_data,
            "metadata": self.metadata
        }
    
    def process_metadata(self):
        pass
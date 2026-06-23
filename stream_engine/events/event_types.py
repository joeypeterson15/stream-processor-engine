event_id_to_type = {
    1: "clicks",
    2: "orders",
}


def get_event_type(event_id):
    return event_id_to_type[event_id]

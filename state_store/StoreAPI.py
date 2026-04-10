from fastapi import APIRouter

class StoreAPI():
    def __init__(self, store):
        self.store = store
        self.router = APIRouter(prefix="/stream-bank")
        self._register_routes()

    def _register_routes(self):
        @self.router.get("/state")
        def get_state():
            return self.store.read_all()

        @self.router.get("/state/{event_type}")
        def get_event_state(event_type: str):
            return self.store.read(event_type)
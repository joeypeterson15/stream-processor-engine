from fastapi import APIRouter, WebSocket, WebSocketDisconnect

class StoreAPI():
    def __init__(self, store):
        self.store = store
        self.router = APIRouter(prefix="/stream-store")
        self._register_routes()

    def _register_routes(self):
        @self.router.get("/state")
        def get_state():
            return self.store.read_all()

        @self.router.get("/state/{event_type}")
        def get_event_state(event_type: str):
            return self.store.read(event_type)

        @self.router.websocket("/ws")
        async def ws_state(websocket: WebSocket):
            await websocket.accept()
            self.store.add_connection(websocket)
            try:
                await websocket.send_json(self.store.read_all())
                while True:
                    # Keep the socket open; we don't require inbound messages.
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.store.remove_connection(websocket)
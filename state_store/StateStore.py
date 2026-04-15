# class StateStore():
#     def __init__(self):
#         self.store = {}

#     def write(self, event_type, data):
#         self.store[event_type] = data

#     def read_all(self):
#         return self.store

#     def read(self, event_type):
#         return self[event_type]


import asyncio
from typing import Any

from starlette.websockets import WebSocket

class StateStore():
    def __init__(self):
        self.state = {}
        self.connections: set[WebSocket] = set()
        self._dirty = False # Locking store for writes/reads

    def add_connection(self, websocket: WebSocket) -> None:
        self.connections.add(websocket)

    def remove_connection(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    def write(self, key: str, data: Any):
        self.state[key] = data
        self._dirty = True

    def read(self, event_type):
        prefix = f"{event_type}:"
        return {k: v for k, v in self.state.items() if k.startswith(prefix)}

    def read_all(self):
        return self.state

    async def broadcaster(self):
        while True:
            if self._dirty and self.connections:
                dead: list[WebSocket] = []
                for connection in list(self.connections):
                    try:
                        await connection.send_json(self.state)
                    except Exception:
                        dead.append(connection)
                for connection in dead:
                    self.remove_connection(connection)
                self._dirty = False
            await asyncio.sleep(0.1)
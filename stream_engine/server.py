from typing import Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel, Field
from stream_engine.events.handlers.BaseHandler import BaseHandler
from state_store.StateStore import StateStore
from state_store.StoreAPI import StoreAPI

import asyncio

class PostEventRequest(BaseModel):
    event_id: int = Field(..., ge=1)
    payload: Dict[str, Any]


class PostEventResponse(BaseModel):
    ok: bool
    event_id: int

def create_app() -> FastAPI:
    store = StateStore()
    base_handler = BaseHandler()
    store_api = StoreAPI(store)

    app = FastAPI(title="Stream Processor Engine")
    app.include_router(store_api.router)

    @app.on_event("startup")
    async def startup():
        asyncio.create_task(store.broadcaster())

    @app.post("/event", response_model=PostEventResponse)
    def post_event(body: PostEventRequest) -> PostEventResponse:
        base_handler.process(body.event_id, body.payload, store)
        return PostEventResponse(ok=True, event_id=body.event_id)

    return app


app = create_app()
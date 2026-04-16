from typing import Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel, Field
import httpx

from stream_engine.events.event_types import get_event_type
from stream_engine.handler_registry import handler_endpoints_by_event_type
from state_store.StateStore import StateStore
from state_store.StoreAPI import StoreAPI
from stream_engine.supervisor import create_supervisor_router, supervisor_loop

import asyncio

class PostEventRequest(BaseModel):
    event_id: int = Field(..., ge=1)
    payload: Dict[str, Any]


class PostEventResponse(BaseModel):
    ok: bool
    event_id: int

def create_app() -> FastAPI:
    store = StateStore()
    store_api = StoreAPI(store)
    endpoints_by_type = handler_endpoints_by_event_type()

    app = FastAPI(title="Stream Processor Engine")
    app.include_router(store_api.router)
    app.include_router(create_supervisor_router())

    @app.on_event("startup")
    async def startup():
        asyncio.create_task(store.broadcaster())
        asyncio.create_task(supervisor_loop())

    @app.post("/event", response_model=PostEventResponse)
    async def post_event(body: PostEventRequest) -> PostEventResponse:
        event_type = get_event_type(body.event_id)
        handler_urls = endpoints_by_type.get(event_type, [])

        async with httpx.AsyncClient(timeout=2.0) as client:
            tasks = [
                client.post(
                    url.rstrip("/") + "/process",
                    json={"event_id": body.event_id, "payload": body.payload, "event_type": event_type},
                )
                for url in handler_urls
            ]
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                # Best-effort: failures will be handled by supervisor restarting containers.
                for r in results:
                    if isinstance(r, Exception):
                        continue
                    try:
                        r.raise_for_status()
                    except Exception:
                        pass
        return PostEventResponse(ok=True, event_id=body.event_id)

    return app


app = create_app()
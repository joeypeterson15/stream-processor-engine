from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from events.event_types import get_event_types
from events.handlers.base_handler import BaseHandler

class PostEventRequest(BaseModel):
    event_id: str = Field(..., min_length=1)
    event: Dict[str, Any]


class PostEventResponse(BaseModel):
    ok: bool
    event_id: str


app = FastAPI(title="Stream Processor Engine")


@app.post("/event", response_model=PostEventResponse)
def post_event(body: PostEventRequest) -> PostEventResponse:
    event_types = get_event_types(body.event_id)
    BaseHandler.process()
    
    # Hook your processing pipeline here (e.g. Engine.process_event(body.event_id, body.event))
    return PostEventResponse(ok=True, event_id=body.event_id)
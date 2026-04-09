from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field


class PostEventRequest(BaseModel):
    event_id: str = Field(..., min_length=1)
    event: Dict[str, Any]


class PostEventResponse(BaseModel):
    ok: bool
    event_id: str


app = FastAPI(title="Stream Processor Engine")


@app.post("/event", response_model=PostEventResponse)
def post_event(body: PostEventRequest) -> PostEventResponse:
    # Hook your processing pipeline here (e.g. Engine.process_event(body.event_id, body.event))
    return PostEventResponse(ok=True, event_id=body.event_id)


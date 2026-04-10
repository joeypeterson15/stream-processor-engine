from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from events.handlers.BaseHandler import BaseHandler

from state_store.StateStore import StateStore

class PostEventRequest(BaseModel):
    event_id: str = Field(..., min_length=1)
    payload: Dict[str, Any]


class PostEventResponse(BaseModel):
    ok: bool
    event_id: str

# Default Port: 8000
# Default Host: 127.0.0.1 (localhost)
# Local URL: http://127.0.0.1:8000
store = StateStore()
base_handler = BaseHandler(store)
app = FastAPI(title="Stream Processor Engine")

@app.post("/event", response_model=PostEventResponse)
def post_event(body: PostEventRequest) -> PostEventResponse:
    base_handler.process(body.event_id, body.payload)
    
    # Hook your processing pipeline here (e.g. Engine.process_event(body.event_id, body.event))
    return PostEventResponse(ok=True, event_id=body.event_id)
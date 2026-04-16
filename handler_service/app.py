import os
from importlib import import_module
from typing import Any, Dict, Optional, Tuple, Type

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field


def _parse_import_spec(spec: str) -> Tuple[str, str]:
    """
    Accepts either:
      - "some.module:ClassName"
      - "some.module.ClassName"
    """
    s = spec.strip()
    if ":" in s:
        mod, cls = s.split(":", 1)
        return mod.strip(), cls.strip()
    if "." not in s:
        raise ValueError(f"Invalid HANDLER_IMPORT={spec!r}. Expected 'module:Class' or 'module.Class'.")
    mod, cls = s.rsplit(".", 1)
    return mod.strip(), cls.strip()


def _load_handler_class(import_spec: str) -> Type[Any]:
    mod_name, cls_name = _parse_import_spec(import_spec)
    mod = import_module(mod_name)
    cls = getattr(mod, cls_name, None)
    if cls is None:
        raise ValueError(f"Could not find class {cls_name!r} in module {mod_name!r}")
    return cls


class StoreClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def write(self, key: str, data: Any) -> None:
        url = f"{self.base_url}/stream-store/write"
        # Small timeout; handler should stay snappy.
        httpx.post(url, json={"key": key, "data": data}, timeout=2.0).raise_for_status()


class ProcessEventRequest(BaseModel):
    event_id: int = Field(..., ge=1)
    payload: Dict[str, Any]
    event_type: str = Field(..., min_length=1)


class ProcessEventResponse(BaseModel):
    ok: bool


def create_app() -> FastAPI:
    handler_import = os.environ.get("HANDLER_IMPORT", "").strip()
    if not handler_import:
        raise RuntimeError("HANDLER_IMPORT env var is required (e.g. stream_engine.events...:ClickEventHandler)")

    store_base_url = os.environ.get("STORE_BASE_URL", "http://engine:8000").strip()

    handler_cls = _load_handler_class(handler_import)
    handler = handler_cls()
    store = StoreClient(store_base_url)

    app = FastAPI(title=f"Handler Service ({handler_cls.__name__})")

    @app.get("/health")
    def health():
        return {"ok": True, "handler": handler_cls.__name__}

    @app.post("/process", response_model=ProcessEventResponse)
    def process_event(body: ProcessEventRequest) -> ProcessEventResponse:
        handler.process_event(body.event_id, body.payload, store, body.event_type)
        return ProcessEventResponse(ok=True)

    return app


app = create_app()


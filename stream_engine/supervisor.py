import asyncio
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from stream_engine.handler_registry import HandlerSpec, get_handler_specs


def _docker_client():
    try:
        import docker  # type: ignore

        return docker.from_env()
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Docker client unavailable. If running in Docker, mount /var/run/docker.sock and install python 'docker' package."
        ) from e


class HandlerStatus(BaseModel):
    key: str
    container_name: str
    endpoint_url: str
    handler_import: str
    image: str
    status: str
    container_id: Optional[str] = None


class HandlersStatusResponse(BaseModel):
    handlers: List[HandlerStatus]


def _get_container_status(spec: HandlerSpec) -> HandlerStatus:
    client = _docker_client()
    try:
        c = client.containers.get(spec.container_name)
        status = c.status  # "running", "exited", ...
        return HandlerStatus(
            key=spec.key,
            container_name=spec.container_name,
            endpoint_url=spec.endpoint_url,
            handler_import=spec.handler_import,
            image=spec.image,
            status=status,
            container_id=c.id,
        )
    except Exception:
        return HandlerStatus(
            key=spec.key,
            container_name=spec.container_name,
            endpoint_url=spec.endpoint_url,
            handler_import=spec.handler_import,
            image=spec.image,
            status="missing",
            container_id=None,
        )


def _ensure_container_running(spec: HandlerSpec) -> Dict[str, Any]:
    client = _docker_client()

    # If container exists, try to start it if not running.
    try:
        c = client.containers.get(spec.container_name)
        if c.status != "running":
            c.start()
        return {"action": "started_existing", "container_id": c.id, "status": c.status}
    except Exception:
        pass

    network = os.environ.get("SUPERVISOR_DOCKER_NETWORK", "").strip() or None
    store_base_url = os.environ.get("STORE_BASE_URL", "http://engine:8000").strip()

    c = client.containers.run(
        image=spec.image,
        name=spec.container_name,
        detach=True,
        environment={
            "HANDLER_IMPORT": spec.handler_import,
            "STORE_BASE_URL": store_base_url,
        },
        ports={"9000/tcp": None},
        network=network,
        restart_policy={"Name": "unless-stopped"},
        labels={"stream_processor_engine": "handler", "handler_key": spec.key},
    )
    return {"action": "created", "container_id": c.id, "status": c.status}


def create_supervisor_router() -> APIRouter:
    router = APIRouter(prefix="/supervisor", tags=["supervisor"])

    @router.get("/handlers", response_model=HandlersStatusResponse)
    def list_handlers():
        specs = get_handler_specs()
        try:
            statuses = [_get_container_status(s) for s in specs]
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        return HandlersStatusResponse(handlers=statuses)

    @router.post("/reconcile")
    def reconcile():
        specs = get_handler_specs()
        try:
            results = {s.key: _ensure_container_running(s) for s in specs}
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))
        return {"ok": True, "results": results}

    return router


async def supervisor_loop(poll_seconds: float = 2.0) -> None:
    """
    Best-effort loop: if a handler is missing/exited, re-create/start it.
    """
    enabled = os.environ.get("SUPERVISOR_ENABLE", "1").strip() not in {"0", "false", "False"}
    if not enabled:
        return

    specs = get_handler_specs()
    while True:
        try:
            for spec in specs:
                _ensure_container_running(spec)
        except Exception:
            # swallow errors; next iteration will retry
            pass
        await asyncio.sleep(poll_seconds)


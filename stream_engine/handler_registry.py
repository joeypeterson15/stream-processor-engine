import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class HandlerSpec:
    key: str
    handler_import: str
    endpoint_url: str
    container_name: str
    image: str


DEFAULT_IMAGE = os.environ.get("HANDLER_IMAGE", "stream_processor_engine-handler:latest")


def default_handler_specs() -> List[HandlerSpec]:
    # Defaults assume docker compose service DNS names.
    return [
        HandlerSpec(
            key="clicks-by-user",
            handler_import="stream_engine.events.handlers.clicks.ClickEventHandler:ClickEventHandler",
            endpoint_url=os.environ.get("HANDLER_CLICKS_URL", "http://handler-clicks:9000"),
            container_name=os.environ.get("HANDLER_CLICKS_CONTAINER", "handler-clicks"),
            image=DEFAULT_IMAGE,
        ),
        HandlerSpec(
            key="clicks-global",
            handler_import="stream_engine.events.handlers.clicks.GlobalClicksEventHandler:GlobalClicksEventHandler",
            endpoint_url=os.environ.get("HANDLER_GLOBAL_CLICKS_URL", "http://handler-global-clicks:9000"),
            container_name=os.environ.get("HANDLER_GLOBAL_CLICKS_CONTAINER", "handler-global-clicks"),
            image=DEFAULT_IMAGE,
        ),
        HandlerSpec(
            key="orders-by-product",
            handler_import="stream_engine.events.handlers.orders.OrderEventHandler:OrderEventHandler",
            endpoint_url=os.environ.get("HANDLER_ORDERS_URL", "http://handler-orders:9000"),
            container_name=os.environ.get("HANDLER_ORDERS_CONTAINER", "handler-orders"),
            image=DEFAULT_IMAGE,
        ),
        HandlerSpec(
            key="orders-global",
            handler_import="stream_engine.events.handlers.orders.GlobalOrdersEventHandler:GlobalOrdersEventHandler",
            endpoint_url=os.environ.get("HANDLER_GLOBAL_ORDERS_URL", "http://handler-global-orders:9000"),
            container_name=os.environ.get("HANDLER_GLOBAL_ORDERS_CONTAINER", "handler-global-orders"),
            image=DEFAULT_IMAGE,
        ),
    ]


def load_handler_specs_from_env() -> Optional[List[HandlerSpec]]:
    """
    Optional override via HANDLER_SPECS_JSON.
    Format: [{key, handler_import, endpoint_url, container_name, image?}, ...]
    """
    raw = os.environ.get("HANDLER_SPECS_JSON", "").strip()
    if not raw:
        return None

    data = json.loads(raw)
    specs: List[HandlerSpec] = []
    for item in data:
        specs.append(
            HandlerSpec(
                key=item["key"],
                handler_import=item["handler_import"],
                endpoint_url=item["endpoint_url"],
                container_name=item["container_name"],
                image=item.get("image", DEFAULT_IMAGE),
            )
        )
    return specs


def get_handler_specs() -> List[HandlerSpec]:
    return load_handler_specs_from_env() or default_handler_specs()


def handler_endpoints_by_event_type() -> Dict[str, List[str]]:
    """
    The engine fans out by event_type ("clicks"/"orders").
    We infer membership by handler_import module path.
    """
    out: Dict[str, List[str]] = {"clicks": [], "orders": []}
    for spec in get_handler_specs():
        if ".clicks." in spec.handler_import:
            out["clicks"].append(spec.endpoint_url)
        elif ".orders." in spec.handler_import:
            out["orders"].append(spec.endpoint_url)
    return out


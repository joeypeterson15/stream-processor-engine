import argparse
import asyncio
import random
import string
import time
from typing import Any, Dict

import httpx

def _rand_id(prefix: str, n: int = 6) -> str:
    return prefix + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def make_click_event() -> Dict[str, Any]:
    return {
        "event_id": 1,
        "payload": {
            "timestamp": time.time(),
            "prod_id": random.choice(["p1", "p2", "p3", "p9"]),
            "session_id": _rand_id("s_", 6),
            "user_id": random.choice(["u1", "u2", "u3", "u9"]),
        },
    }


def make_order_event() -> Dict[str, Any]:
    return {
        "event_id": 2,
        "payload": {
            "timestamp": time.time(),
            "prod_id": random.choice(["p1", "p2", "p3", "p9"]),
        },
    }


async def run(base_url: str, interval_ms: int, clicks_weight: int, orders_weight: int) -> None:
    url = base_url.rstrip("/") + "/event"
    weights = [("click", clicks_weight), ("order", orders_weight)]

    timeout = httpx.Timeout(5.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            kind = random.choices([k for k, _ in weights], weights=[w for _, w in weights], k=1)[0]
            body = make_click_event() if kind == "click" else make_order_event()

            try:
                resp = await client.post(url, json=body)
                resp.raise_for_status()
                data = resp.json()
                print(f"{time.strftime('%H:%M:%S')} sent={kind} event_id={data.get('event_id')} ok={data.get('ok')}")
            except Exception as e:
                print(f"{time.strftime('%H:%M:%S')} error sending {kind}: {e}")

            await asyncio.sleep(interval_ms / 1000.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Random fake-event producer for Stream Processor Engine")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL (default: http://localhost:8000)")
    parser.add_argument("--interval-ms", type=int, default=400, help="Milliseconds between events (default: 400)")
    parser.add_argument("--clicks-weight", type=int, default=7, help="Relative probability of click events (default: 7)")
    parser.add_argument("--orders-weight", type=int, default=3, help="Relative probability of order events (default: 3)")
    args = parser.parse_args()
    # print(args)

    asyncio.run(run(args.base_url, args.interval_ms, args.clicks_weight, args.orders_weight))


if __name__ == "__main__":
    main()


# Stream Processor Engine

## Dockerized handlers

Handlers now run as **separate containers** and communicate back to the engine’s state store via HTTP.

### Start backend + handler containers

Prereqs: Docker Desktop (or Docker Engine) with `docker compose`.

```bash
docker compose up --build
```

This starts:
- `engine` on `http://localhost:8000`
- one container per handler (`handler-clicks`, `handler-global-clicks`, `handler-orders`, `handler-global-orders`)

### Supervisor API (container status + auto-recreate)

- `GET /supervisor/handlers`: list expected handler containers + status
- `POST /supervisor/reconcile`: start/create any missing/down handler containers

The engine also runs a small reconcile loop on startup (best-effort).

### Run the frontend

```bash
cd app/stream_app_engine
npm install
npm start
```

Open `http://localhost:3000` to see:
- live stream state (via WebSocket)
- **handler container status** (polls `/supervisor/handlers`)


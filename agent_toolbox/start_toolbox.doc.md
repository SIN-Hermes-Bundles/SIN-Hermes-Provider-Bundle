# start_toolbox.py

FastAPI App Entry Point für die SINator Agent Toolbox. Registriert alle Routen, konfiguriert CORS/Auth-Middleware, und startet Uvicorn auf Port 8000.

## Berührt

- `agent_toolbox/api/routes/*` — 5 Router werden hier registriert (gmx, fireworks, pool, lease, rotation, config)
- `pool_manager.py` — Lebenszeit-Management via `get_pool_manager()`
- `config_manager.py` — `get_config()` wird für Auth/Setup genutzt
- Dashboard (Tauri) — `GET /dashboard`, `GET /health`, `GET /pool/stats`

## Wichtige Entscheidungen

- **Uvicorn direkt:** App startet via `python start_toolbox.py` (vereinfacht Deployment)
- **Kein Gunicorn:** Single-Process Uvicorn — ausreichend für lokalen Proxy-Betrieb
- **Auth-Middleware:** Custom Middleware — prüft `Bearer <token>` für ALLE `/api/*` Requests
- **Public Prefixes:** `/api/v1/pool/`, `/api/v1/pool-lease`, `/api/v1/rotation/`, `/api/v1/config` — KEIN Auth-Token nötig
- **Auto-Token:** Wenn `SINATOR_AUTH_TOKEN` nicht gesetzt → zufälliger `sinator-<uuid>` Token (geloggt)
- **Kein CDP Wait:** V15.4 nutzt `chromium.launch()` — kein Running Chrome nötig
- **Kein Auto-Restart:** `reload=False` im Default (explizit via `TOOLBOX_RELOAD=true`)

## Flow

```
python agent_toolbox/start_toolbox.py
  → sys.path setup (projekt_root)
  → Logging konfiguriert (stdout + file)
  → FastAPI App mit CORS + Auth Middleware
  → 5 Routen registriert (/api/v1/*)
  → Uvicorn auf :8000 gestartet
```

## Config

```bash
TOOLBOX_PORT=8000       # Default Port
TOOLBOX_HOST=0.0.0.0    # Bind-Adresse
TOOLBOX_RELOAD=false    # Auto-Reload
SINATOR_AUTH_TOKEN=     # Optional: Auth-Token (sonst auto-generated)
```

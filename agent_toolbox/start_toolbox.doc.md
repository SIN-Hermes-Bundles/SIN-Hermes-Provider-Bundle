# start_toolbox.py

FastAPI App Entry Point für die SINator Agent Toolbox. Registriert alle Routen, konfiguriert CORS/Auth-Middleware, und startet Uvicorn auf Port 8000.

## Berührt

- `agent_toolbox/api/routes/*` — Alle 8 Router werden hier registriert (browser, gmx, fireworks, cookies, pool, lease, rotation, config)
- `pool_manager.py` — Lebenszeit-Management via `get_pool_manager()`
- `config_manager.py` — `get_config()` wird für Auth/Setup genutzt
- Dashboard (Tauri) — `GET /dashboard`, `GEt /health`, `GET /pool/stats`
- `browser_manager.py` — Shutdown-Cleanup beim Herunterfahren

## Wichtige Entscheidungen

- **Uvicorn direkt:** Kein `uvicorn` CLI-Befehl — App startet via `python start_toolbox.py` (vereinfacht Deployment)
- **Kein Gunicorn:** Single-Process Uvicorn — ausreichend für lokalen Proxy-Betrieb
- **Auth-Middleware:** Custom Middleware (nicht FastAPI Dependency) — prüft `Bearer <token>` für ALLE `/api/*` Requests
- **Public Prefixes:** `/api/v1/browser/`, `/api/v1/pool/`, `/api/v1/pool-lease`, `/api/v1/rotation/`, `/api/v1/config` — KEIN Auth-Token nötig
- **Auto-Token:** Wenn `SINATOR_AUTH_TOKEN` nicht gesetzt → zufälliger `sinator-<uuid>` Token (geloggt)
- **CDP Wait:** Wartet bis zu `SINATOR_CDP_WAIT` (default 8s) dass Chrome auf Port 9222 bereit ist
- **Kein Auto-Restart:** `reload=False` im Default (explizit via `TOOLBOX_RELOAD=true`)

## Flow

```
python agent_toolbox/start_toolbox.py
  → sys.path setup (projekt_root)
  → Logging konfiguriert (stdout + file)
  → FastAPI App mit CORS + Auth Middleware
  → 8 Routen registriert (/api/v1/*)
  → CDP Port 9222 Check (wait bis Chrome ready)
  → Uvicorn auf :8000 gestartet
```

## Config

```bash
TOOLBOX_PORT=8000       # Default Port
TOOLBOX_HOST=0.0.0.0    # Bind-Adresse
TOOLBOX_RELOAD=false    # Auto-Reload
SINATOR_AUTH_TOKEN=     # Optional: Auth-Token (sonst auto-generated)
SINATOR_CDP_WAIT=8      # Sekunden bis CDP Timeout
```

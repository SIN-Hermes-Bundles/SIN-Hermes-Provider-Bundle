# browser.py (Routes)

Browser Lifecycle API Endpoints: Start, Stop, Status. FastAPI Router unter `/browser/*`. 3 Endpunkte — Wrapper um `BrowserManager`.

## Berührt

- `browser_manager.py` — `get_browser_manager()` Singleton
- `schemas.py` — Browser-Request/Response-Models
- `agent_toolbox/start_toolbox.py` — Registriert diesen Router

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| POST | `/browser/start` | Chrome starten mit Profil + CDP |
| POST | `/browser/stop` | Chrome beenden + Cleanup |
| GET | `/browser/status` | Browser-Status (running, cdp_port, pages) |

## Wichtige Entscheidungen

- **Public (kein Auth):** Alle Browser-Endpoints sind in `public_prefixes` der Auth-Middleware
- **Warm-Start:** Wenn Chrome bereits läuft, verbindet `start` nur — kein Neustart
- **Kein Playwright Context mehr:** `browser_status()` prüft `_context.pages` (nicht mehr vorhanden seit CDP-only Migration)
- **Profil-Konfiguration:** Akzeptiert `profile_name`, `cdp_port`, `headless`, `chrome_path` im Request

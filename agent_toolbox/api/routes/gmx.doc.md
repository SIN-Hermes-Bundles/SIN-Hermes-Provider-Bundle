# gmx.py (Routes)

GMX API Endpoints: Session-Check, Session-Ensure, Alias CRUD, Inbox Open, OTP Read. FastAPI Router unter `/gmx/*`. Delegiert Alias-Operationen primär an standalone gmx-alias-tool API (:8001) mit Fallback auf direkte GmxService-Aufrufe.

## Berührt

- `gmx_service.py` — Session-Check, Email-Addresses, Inbox, OTP — alle via `get_gmx_service()`
- `browser_manager.py` — `_require_browser()` für CDP-Port
- `gmx-alias-tool API (:8001)` — Alias Delete/Create/Rotate delegiert
- `schemas.py` — Alle GMX Response-Models
- `tools/rotate.py` — indirekt via `/rotation/full`

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| POST | `/gmx/session/check` | GMX Session validieren |
| POST | `/gmx/session/ensure` | GMX Login oder Session wiederherstellen |
| POST | `/gmx/email-addresses` | Alias-Verwaltungsseite öffnen |
| POST | `/gmx/alias/delete` | Alias löschen |
| POST | `/gmx/alias/create` | Alias erstellen |
| POST | `/gmx/alias/rotate` | Alias löschen + neu (atomar) |
| POST | `/gmx/inbox/open` | GMX Inbox öffnen |
| POST | `/gmx/otp/read` | OTP aus Inbox lesen (sollte GET sein) |

## Wichtige Entscheidungen

- **Alias über :8001 API delegiert:** gmx-alias-tool läuft auf eigenem Port — Soxhlet Proxy-Probleme mit SPA gelöst
- **Fallback auf GmxService direkt:** Wenn gmx-alias-tool API nicht läuft, nutzt direkte GmxService-Aufrufe (via Playwright)
- **Browser-Prüfung:** `_require_browser()` wirft 400 wenn Chrome nicht via CDP erreichbar
- **Timeout:** 120s für Alias-API-Calls (httpx AsyncClient)
- **⚠️ OTP via CDP:** `read_otp()` nutzt CDP OOPIF für `mailbody-ui.de` — Playwright kann da nicht hin (cross-origin)

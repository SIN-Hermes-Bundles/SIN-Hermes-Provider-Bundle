# schemas.py

Pydantic Request/Response-Modelle für ALLE FastAPI-Endpunkte. 5 Schema-Gruppen: Browser, GMX, Fireworks, Cookie, Pool, Rotation. Garantiert exakte JSON-Strukturen für API-Konsumenten.

## Berührt

- `agent_toolbox/api/routes/*` — Alle Route-Handler importieren Schemas für Input-Validation + Response-Modelle
- `agent_toolbox/start_toolbox.py` — FastAPI App initialisiert OpenAPI/Swagger aus diesen Schemas
- Tauri Dashboard — Verwendet Response-Modelle für TypeScript-Typen (via OpenAPI Spec)

## Schema-Gruppen

| Gruppe | Models | Routes |
|--------|--------|--------|
| **Browser** | BrowserStartRequest/Response, BrowserStopResponse, BrowserStatusResponse | `/browser/start`, `/browser/stop`, `/browser/status` |
| **GMX** | GmxSessionCheckRequest/Response, GmxAliasRequest/Response, GmxOtpRequest/Response, GmxAliasRotateRequest/Response, GmxInboxOpenResponse, GmxEmailAddressesResponse, GmxAliasDeleteResponse | `/gmx/*` |
| **Fireworks** | FireworksRegisterRequest/Response, FireworksApiKeyRequest/Response | `/fireworks/*` |
| **Cookie** | CookieExtractRequest/Response, CookieInjectRequest/Response | `/cookies/*` |
| **Pool** | PoolStatsResponse, PoolAddKeyRequest/Response | `/pool/*` |
| **Rotation** | RotationRequest/Response | `/rotation/full` |

## Wichtige Entscheidungen

- **Pydantic v2:** Alle Models nutzen `BaseModel` mit Field-Validatoren (`ge`, `le`, `default_factory`)
- **`execution_time` Pflichtfeld:** JEDES Response-Model hat `execution_time: str` — für Monitoring/Performance-Tracking
- **`error` Optional:** Nur gesetzt bei `status=error` — NIEMALS in success-responses
- **`steps_completed/failed` Listen:** Rotation/GMX-Responses dokumentieren jeden Schritt
- **Type-Safety:** `from typing import Optional, List, Dict` überall — keine `Any` außer für generische Dicts
- **Backward-Compatible:** Neue Felder sind immer Optional

## Anti-Patterns

| ❌ FALSCH | ✅ RICHTIG |
|-----------|-----------|
| Response ohne execution_time | JEDES Response hat execution_time |
| error-Feld in success | error nur bei status=error |
| Kein default_factory für Listen | `Field(default_factory=list)` |
| Hardcoded Status-Strings | Validierte Enum-Werte |

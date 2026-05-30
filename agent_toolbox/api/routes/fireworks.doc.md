# fireworks.py (Routes)

Fireworks AI API Endpoints: Login + API Key Erstellung. FastAPI Router unter `/fireworks/*`. 2 Endpunkte — minimaler Wrapper um `fireworks_service.py` Funktionen.

## Berührt

- `fireworks_service.py` — `login_fireworks()`, `create_api_key()` (neue Signatur mit Session Reuse)
- `browser_manager.py` — `_require_browser()` für CDP-Port-Prüfung
- `schemas.py` — `FireworksRegisterRequest/Response`, `FireworksApiKeyRequest/Response`
- `pool_manager.py` — indirekt via `create_api_key()`

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| POST | `/fireworks/login` | Login + Onboarding (Playwright + CUA) |
| POST | `/fireworks/apikey` | API Key erstellen (Playwright) |

## Wichtige Entscheidungen

- **Session Reuse (V15.1 FIX):** Wenn `email`+`password` im Request → `login_fireworks()` zuerst → `page+playwright+browser` an `create_api_key()` übergeben
- **Backward-Compatible:** Ohne `email`/`password` → alte Logik (neue Page) — aber Redirect zu `/login` möglich
- **Kein Signup-Endpoint:** nur Login + API Key — Signup läuft direkt via `tools/rotate.py`

## Flow

```
POST /fireworks/login {email, password}
  → login_fireworks(email, password)
  → Playwright Login + CUA Onboarding + Playwright Fallback
  → FireworksRegisterResponse

POST /fireworks/apikey {key_name, email?, password?}
  → Wenn email+password: login_fireworks() → Session Reuse
  → create_api_key(key_name, page=..., playwright=..., browser=...)
  → Playwright API Key Page → Create → Generate → Extract
  → FireworksApiKeyResponse
```

## Fixed (V15.1)

**Vorher:** `create_api_key(request.key_name)` — neue Page, keine Session → `/login` Redirect.
**Nachher:** Wenn `email`+`password` im Request → Login zuerst + Session Reuse. Ohne Credentials → alte Logik.

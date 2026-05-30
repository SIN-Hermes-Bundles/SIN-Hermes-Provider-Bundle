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

- **⚠️ API Route verwendet `create_api_key(request.key_name)` OHNE Session Reuse:** Diese Route erstellt eine neue Page — kein Session Reuse vom Login. Kann zu `/login` Redirect führen!
- **login_fireworks gibt `page, playwright, browser` zurück** (V15.1) aber diese Route ignoriert das — bug wartend
- **Kein Signup-Endpoint:** nur Login + API Key — Signup läuft direkt via `tools/rotate.py`

## Flow

```
POST /fireworks/login {email, password}
  → login_fireworks(email, password)
  → Playwright Login + CUA Onboarding + Playwright Fallback
  → FireworksRegisterResponse

POST /fireworks/apikey {key_name}
  → create_api_key(key_name)  ← ⚠️ NEUE Page, keine Session Reuse!
  → Playwright API Key Page → Create → Generate → Extract
  → FireworksApiKeyResponse
```

## Bug-Warnung

Die `/fireworks/apikey` Route ruft `create_api_key(request.key_name)` OHNE die optionalen Session-Parameter (`page`, `playwright`, `browser`) auf. Wenn diese Route nach `/fireworks/login` aufgerufen wird, hat die neue Page keine Cookies → API Key Seite redirected zu `/login`.

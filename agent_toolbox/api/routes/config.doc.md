# config.py (Routes)

Config API Endpoints: GET + POST für GMX/Fireworks Credentials. Public (kein Auth-Token). 2 Endpunkte — minimaler Wrapper um `config_manager.py`.

## Berührt

- `config_manager.py` — `get_config()` Singleton
- Dashboard Setup-Seite (`/setup`) — nutzt `GET /api/v1/config` + `POST /api/v1/config`
- `tools/rotate.py` — indirekt via Config Manager

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| GET | `/api/v1/config` | Aktuelle Config lesen |
| POST | `/api/v1/config` | Config speichern |

## Flow

```
GET /api/v1/config
  → get_config()
  → {gmx_email, gmx_password, fireworks_password}

POST /api/v1/config {gmx_email, gmx_password, fireworks_password}
  → get_config().save(...)
  → Persistiert in data/config.json
  → {gmx_email, fireworks_password} (Achtung: gmx_password fehlt in Response)
```

## Wichtige Entscheidungen

- **Public (kein Auth):** `/api/v1/config` ist im `public_prefixes` der Auth-Middleware
- **⚠️ POST Response fehlt gmx_password:** `save_config_route()` gibt `ConfigOut(gmx_email=..., fireworks_password=...)` zurück — KEIN `gmx_password`! Bug!
- **Kein PUT / PATCH:** Nur GET + POST — kein partial update
- **ConfigOut vs ConfigIn:** Unterschiedliche Models für Request/Response

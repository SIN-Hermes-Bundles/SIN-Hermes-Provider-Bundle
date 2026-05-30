# proxy/config.py

Proxy-Konfiguration: Ports, Fireworks Base-URL, Lease-Parameter, Retry-Limits. Lädt aus Env-Vars + optionaler JSON-Config-Datei.

## Berührt

- `proxy/server.py` — Nutzt Config für Proxy-Port, Fireworks-URL, Lease-TTL
- `proxy/pool_client.py` — Nutzt Config für Pool-API-URL und Lease-Parameter
- `proxy/start-multi.sh` — Setzt Port via `SIN_PROXY_PORT` Env
- `~/.sin-pool/config.json` — Persistierte Config (optional)

## Config Keys

| Key | Env | Default | Beschreibung |
|-----|-----|---------|-------------|
| `proxy_port` | `SIN_PROXY_PORT` | 8888 | Proxy-Listen-Port |
| `pool_api_url` | `SIN_POOL_API_URL` | `http://localhost:8000/api/v1` | Pool-API Endpunkt |
| `fireworks_base` | — | `https://api.fireworks.ai/inference/v1` | Fireworks API |
| `lease_ttl_seconds` | `SIN_LEASE_TTL` | 1800 | Key-Lease Dauer |
| `lease_backup` | `SIN_LEASE_BACKUP` | false | Backup-Key beim Lease |
| `max_retries` | `SIN_MAX_RETRIES` | 3 | Interne Retries |

## Wichtige Entscheidungen

- **Env-First:** Env-Vars haben Vorrang vor Config-Datei — 12-Factor App Prinzip
- **Tunnel URL Auto-Detect:** `pool_api_url` wird automatisch aus `tunnel-url.txt` gelesen falls vorhanden
- **Cache-Dir:** `~/.sin-pool/` (oder via `SIN_CACHE_DIR`)
- **Kein Data-Dir:** Config ist separat vom Pool-Data-Dir

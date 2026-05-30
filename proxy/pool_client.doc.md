# pool_client.py

HTTP Client für Proxy → Pool-API Kommunikation. Wrapper um httpx mit Lease/Return/Report/Stats Methoden. Jeder Proxy erstellt eine eigene PoolClient-Instanz.

## Berührt

- `proxy/config.py` — `load_config()` für API-URL und Lease-TTL
- `proxy/server.py` — Nutzt PoolClient für Key-Management (Lease, Return, Report)
- `agent_toolbox/api/routes/pool.py` — Target-API für alle Methoden
- `pool_manager.py` — Indirekt via Pool-API

## Methods

| Methode | API Call | Zweck |
|--------|----------|-------|
| `lease(leased_to)` | POST /pool/lease | Key atomar leasen |
| `return_key(key_id, lease_id)` | POST /pool/return | Key zurückgeben |
| `report(api_key, key_id, reason)` | POST /pool/report | Bad Key melden + Ersatz |
| `stats()` | GET /pool/stats | Pool-Statistiken |
| `close()` | — | HTTP Client schließen |

## Config / Limits

- **API URL:** `http://localhost:8000/api/v1` (oder via `SIN_POOL_API_URL` env)
- **Lease TTL:** 1800s (30min) — via Config oder `SIN_LEASE_TTL` env
- **HTTP Timeout:** 15s pro Request
- **Retry:** Kein internes Retry (Fehler werden an Proxy weitergegeben)

## Wichtige Entscheidungen

- **Kein Retry:** PoolClient erwartet dass Proxy/Server-Retry-Logik hat — kein Doppel-Retry
- **Atomic Report:** `report()` markiert Key als used UND leaset Ersatz-Key in einer API-Call
- **Silent Errors:** Fehler werden geloggt aber nicht re-raised — Proxy entscheidet was zu tun
- **Shared httpx Client:** Ein Client pro Proxy-Instanz (nicht pro Request) — Connection-Reuse

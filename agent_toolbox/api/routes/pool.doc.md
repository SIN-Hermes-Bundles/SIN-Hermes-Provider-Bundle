# pool.py (Routes)

Pool-Management API Endpunkte: Stats, Add, Use, Lease, Return, Report, Events (SSE), Health, Reveal, Migrate, Delete. Haupt-API für Proxy-Key-Management und Dashboard.

## Berührt

- `pool_manager.py` — Alle Route-Handler delegieren an PoolManager
- `keychain_store.py` — `/reveal/{key_id}` und `/health` hydratisieren Keys aus Keychain
- `proxy/server.py` — Holt Keys via `/pool/lease` + meldet via `/pool/report`
- `proxy/pool_client.py` — HTTP Client für die Pool-API
- Tauri Dashboard — `/pool/stats`, `/pool/events` (SSE), `/pool/health`

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| GET | `/pool/stats` | Pool-Statistiken (total/used/suspended/available) |
| POST | `/pool/add` | API-Key zum Pool hinzufügen |
| POST | `/pool/use` | Key als used markieren |
| GET | `/pool/key` | Nächsten verfügbaren Key (hydratisiert) |
| POST | `/pool/lease` | Key atomar leasen (TTL, locked) |
| POST | `/pool/return` | Geleasten Key zurückgeben |
| POST | `/pool/report` | Bad Key melden + atomar Ersatz leasen |
| GET | `/pool/events` | SSE Stream (Dashboard Live-Updates) |
| GET | `/pool/health` | Alle Keys via Fireworks API validieren |
| GET | `/pool/reveal/{key_id}` | Echten API-Key aus Keychain (nur localhost) |
| POST | `/pool/migrate-to-keychain` | Plaintext → Keychain Migration |
| DELETE | `/pool/{key_id}` | Key aus Pool löschen |

## Wichtige Entscheidungen

- **Atomic Report+Lease:** `report_key()` markiert Key als used UND leaset Ersatz-Key in EINER Operation — verhindert Double-Key-Waste
- **SSE nicht Polling:** Dashboard bekommt Live-Updates via EventSource — kein 5s-Interval-Polling
- **Health ist Read-Only:** Markiert KEINE Keys mehr als used (Side-Effect-Fix vom 2026-05-23)
- **Reveal ist Local-Only:** `/reveal/{key_id}` gibt Klartext-Key zurück — NUR für localhost/Dashboard
- **`/pool-lease` GET:** Separater Endpunkt für Dashboard-Kompatibilität (gleiche Logik wie POST `/pool/lease`)

## Flow

```
Proxy startet → POST /pool/lease (ttl=1800) → api_key + lease_id
Request kommt → Key wird verwendet
413/429/412 → POST /pool/report (key_id, reason) → new_key atomar
Key nicht mehr benötigt → POST /pool/return (key_id)
```

## SSE Events

| Event | Daten | Trigger |
|-------|-------|---------|
| `key_leased` | key_id, lease_id, expires_at | Proxy leased Key |
| `key_returned` | key_id | Proxy returned Key |
| `key_swapped` | old_key_id, new_key_id | Bad Key gemeldet |
| `stats` | total, used, available | Alle 30s (periodisch) |

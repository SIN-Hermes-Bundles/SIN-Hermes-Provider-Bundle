# pool_manager.py

Fireworks API Key Pool Management. JSON-basierte Key-Verwaltung mit Lease/Report-Atomizität, Staleness-Erkennung und Pool-Stats.

## Berührt

- `proxy/server.py` — Leased Keys für Requests, reportet Status zurück
- `fireworks_service.py` — Speichert neue Keys nach Signup
- `api/routes/pool.py` — Pool-Stats API Endpoints
- `tools/rotate.py` — `add_key()` nach Rotation

## Config

- `POOL_FILE: data/fireworksai-pool.json`
- Key States: `available`, `used`, `suspended`
- Stats: `available = total - used - suspended` (kein `leased` Feld)
- Atomic Report+Lease: `report_key()` leaset Ersatz-Key im selben Lock wie suspend

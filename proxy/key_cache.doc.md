# key_cache.py

Proxy-seitiger Key-Cache: Speichert den aktuell geleasten API-Key (primary) + Backup-Key in `~/.sin-pool/`. File-basierte Persistenz — überlebt Proxy-Neustarts. Automatische Lease-Expiry-Prüfung.

## Berührt

- `proxy/config.py` — `CACHE_DIR` = `~/.sin-pool/`
- `proxy/server.py` — Nutzt KeyCache für Key-Management (Lease, Return, Report)
- `proxy/pool_client.py` — Holt neue Keys bei Cache-Leer oder Swap

## Config / Limits

- **Cache-Dir:** `~/.sin-pool/` (via `SIN_CACHE_DIR` env)
- **Files:** `current-key.json` (primary) + `backup-key.json` (backup)
- **Lease-Expiry:** Automatic — `get_primary()` prüft `expires_at` Timestamp
- **Request-Counter:** `request_count` wird mit jedem `get_primary()` inkrementiert

## Wichtige Entscheidungen

- **File-Persistenz:** Key-Cache überlebt Proxy-Neustarts — kein Memory-Only Cache
- **Kein Locking:** Single-Threaded asyncio — keine Race-Conditions
- **Backup-Promotion:** `promote_backup()` macht Backup zum Primary — nur wenn Backup nicht abgelaufen
- **Expiry-Check:** `get_primary()` prüft `expires_at` Timestamp und löscht gecachete Files wenn abgelaufen
- **Clear-On-Error:** `clear_primary()` / `clear_all()` für Swap-Szenarien

## Flow

```
Proxy startet → KeyCache._load() → cached key from disk
Falls kein cached key oder expired:
  → PoolClient.lease() → neuer Key
  → KeyCache.set_primary(key_info) → saved to disk
  
Request kommt:
  → KeyCache.get_primary() → prüft expiry → api_key
  → request_count++

413/429/412 Fehler:
  → KeyCache.promote_backup() (falls vorhanden)
  → ODER KeyCache.clear_primary() + PoolClient.report() → neuer Key

Proxy stoppt:
  → Key bleibt auf Disk → überlebt Neustart
```

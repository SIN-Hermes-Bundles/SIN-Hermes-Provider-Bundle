# keychain_store.py

macOS Keychain-backed secret store für API Keys. Pool JSON speichert nur Metadaten — die eigentlichen API Keys leben als generische Passwörter im macOS Keychain unter dem Service `com.sinator.pool`.

## Berührt

- `pool_manager.py` — `add_key()` speichert Key in Keychain, `get_available_key()` hydratisiert via `retrieve_key()`
- `agent_toolbox/api/routes/pool.py` — `/reveal/{key_id}` hydratisiert Key aus Keychain
- `data/fireworksai-pool.json` — api_key Feld enthält `"STORED_IN_KEYCHAIN"` Sentinel statt Klartext

## Config / Limits

- **Service Name:** `com.sinator.pool`
- **Account Name:** key_id (UUID)
- **Sentinel:** `"STORED_IN_KEYCHAIN"` — ersetzt api_key in Pool-JSON
- **Timeout:** 10s pro `security` CLI Call
- **Migration:** `migrate_pool()` — one-shot von Plaintext → Keychain

## Wichtige Entscheidungen

- **KEYCHAIN IST PFLICHT:** API Keys dürfen NIEMALS im Klartext in Pool-JSON gespeichert werden. Der `security` CLI ist der einzige Weg.
- **Hydration:** `hydrate_keys()` ersetzt Sentinel-Werte mit echten Keys aus Keychain — nur für aktive Verwendung
- **Migration-Ready:** `migrate_pool()` konvertiert alte Plaintext-Pools automatisch
- **macOS Only:** Keychain ist macOS-spezifisch — kein Cross-Plattform-Support
- **`security` CLI subprocess:** Kein macOS Keychain Python SDK verwendet — reiner `subprocess.run(["security", ...])`
- **NIEMALS `security` interactive-shell prompts ignorieren:** Height-Prompt kann Keychain sperren

## Flow

```python
# Store
store_key(key_id="uuid-1234", api_key="fw_xxx")
# → security add-generic-password -s com.sinator.pool -a uuid-1234 -w fw_xxx -U

# Retrieve
api_key = retrieve_key("uuid-1234")
# → security find-generic-password -s com.sinator.pool -a uuid-1234 -w

# Hydrate Pool
hydrate_keys([{"id": "uuid-1234", "api_key": "STORED_IN_KEYCHAIN"}])
# → [{"id": "uuid-1234", "api_key": "fw_xxx_real"}]

# Migration
migrate_pool(pool_path, dry_run=False)
# → Liest plaintext Keys → speichert in Keychain → ersetzt mit SENTINEL
```

## Security

- **Kein Echo:** API Keys werden nie in Logs ausgegeben
- **Subprocess Clean-up:** `_run_security` hat 10s Timeout
- **Log-Truncation:** Key-Prefix wird auf 8 Zeichen beschränkt

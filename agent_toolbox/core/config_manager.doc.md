# config_manager.py

SINator Runtime Configuration (GMX + Fireworks Credentials). Singleton mit Lazy-Load aus `data/config.json`. Dient als Single Source of Truth für alle Credentials die rotate.py benötigt.

## Berührt

- `tools/rotate.py` — liest Config via `get_config()` für `--gmx-email --gmx-password --password`
- `agent_toolbox/api/routes/config.py` — `GET/POST /api/v1/config` (public, kein Auth)
- `agent_toolbox/api/routes/rotation.py` — `/rotation/full` liest Config via `get_config()`
- `data/config.json` — persistierte JSON-Datei mit 3 Feldern

## Config / Limits

- **Fields:** `gmx_email`, `gmx_password`, `fireworks_password`
- **Defaults (Hardcoded-Fallback):** delqhi@gmx.de / ZOE.jerry2024 / ZOE.jerry2024!
- **Singleton:** `get_config()` — nur eine Instanz pro Prozess
- **File:** `data/config.json` (projekt-relativ)

## Wichtige Entscheidungen

- **NIE Hardcoded Credentials im Code:** Rotate liest via `get_config()`, nicht via `os.environ` oder Konstanten
- **Config ist public (kein Auth-Token):** Dashboard Setup-Seite brauchte Zugriff → `/api/v1/config` in `public_prefixes`
- **Lazy-Load:** Singleton wird erst bei erstem `get_config()` initialisiert
- **Fallback-Defaults:** Wenn `config.json` nicht existiert, werden die im Code stehenden Defaults verwendet

## Flow

```python
from agent_toolbox.core.config_manager import get_config

cfg = get_config()  # Lädt aus data/config.json (oder Defaults)
cfg.gmx_email       # "delqhi@gmx.de"
cfg.gmx_password    # "ZOE.jerry2024"
cfg.fireworks_password  # "ZOE.jerry2024!"

# Speichern (via API oder Dashboard)
cfg.save(gmx_email="neu@gmx.de", gmx_password="...", fireworks_password="...")
```

## API

```
GET  /api/v1/config     → {"gmx_email": "...", "gmx_password": "...", "fireworks_password": "..."}
POST /api/v1/config     → {gmx_email, gmx_password, fireworks_password} → 200 OK
```

Kein Auth-Token nötig (in `public_prefixes`).

# SINator — Fireworks AI Key Pool

[![GitNexus](https://img.shields.io/badge/GitNexus-knowledge%20graph-8B5CF6)](.gitnexus/)

> **⚠️ GitNexus-Pflicht:** Bevor du Code in diesem Repo änderst, MUSST du `gitnexus_impact()` (Blast Radius) und `gitnexus_detect_changes()` (vor Commit) ausführen. Siehe [GitNexus Guide](.gitnexus/).

Automated GMX alias rotation → Fireworks AI account → API key pool.
OpenAI-compatible proxy with automatic key rotation on rate-limits.

**Backend Port:** `8000` | **Pool-Router:** `9998` | **Dashboard Repo:** [SINator-dashboard](https://github.com/SIN-Rotator/SINator-dashboard) | **HeyPiggy Repo:** [SINator-heypiggy](https://github.com/SIN-Rotator/SINator-heypiggy) | **[📖 Installationsanleitung](INSTALL.md)**

## EINE Base-URL — Pool-Router mit Auto-Failover

**Es gibt nur EINEN Endpunkt.** Der Pool-Router verteilt Requests automatisch auf 10 lokale Proxys (8888-8897), jeder mit eigenem API-Key aus dem Pool. Bei 413/429/412/5xx springt der Router zum nächsten Proxy.

| Zugriff | Base URL |
|---------|----------|
| **Standard (alle Clients)** | `https://sinatorpool-router.delqhi.com/inference/v1` |

**Kein manuelles Pool-Wechseln mehr.** Der Router macht alles automatisch.

### Auto-Failover

| Status | Reaktion |
|--------|----------|
| 413 Payload Too Large | Nächster Proxy |
| 429 Rate Limit | Nächster Proxy |
| 412 Account Suspended | Nächster Proxy |
| 500/502/503/504 Server Error | Nächster Proxy |
| Alle Pools gleicher Fehler | Status-Code durchreichen (pass-through) |
| Proxy 3 Fehler in 60s | Cooldown — 60s Pause |

### Backend: 10 Proxys (lokal, 8888-8897)

Jeder Proxy ist eine eigene aiohttp-Instanz mit charset-Fix, eigenem API-Key aus dem Pool (218 Keys), und launchd-Autostart.

## Installation

**→ [INSTALL.md](INSTALL.md)** — Prozedurale Schritt-für-Schritt-Anleitung mit Prerequisites-Checks, Verifikation nach jedem Schritt, und Fehlerbehebung.

```bash
# Quick-Start (nach README reichen 3 Befehle):
python3 agent_toolbox/start_toolbox.py          # Backend :8000
bash proxy/start-multi.sh                        # Proxys + Router
python3 tools/rotate.py                          # Ersten Key holen
```

---

## Architecture

```
Clients (opencode, Cursor, Hermes, etc.)
  ↓ OpenAI-compatible API
Pool-Router (:9998, ThreadingMixIn)
  ↓ Auto-Failover über 10 Proxys
Pool Proxys (:8888-:8897, aiohttp SSE)
  ↓ Key rotation + silent swap
Backend (:8000, FastAPI)
  ↓ PoolManager + ConfigManager
Chrome + Playwright + CUA (Onboarding only)
  ↓ Browser automation
GMX → Fireworks AI → API Key
```

**Services (macOS LaunchAgents):**

| Service | Port | Purpose |
|---------|------|---------|
| `com.sinator.backend` | :8000 | FastAPI Backend |
| `com.sinator.pool-router` | :9998 | Pool-Router mit Auto-Failover |
| `com.sinator.pool-proxy-{8888..8897}` | :8888-:8897 | 10× OpenAI-compatible proxies with silent swap |
| `com.sinator.pages` | :8040 | Landing page |

---

## Dashboard + HeyPiggy Integration

Dieses Repo ist der Fireworks-Backend. Das vollständige System besteht aus drei Repos:

| Repo | Port | Funktion |
|------|------|----------|
| **SINator-fireworksai** (dieses) | `:8000` | Fireworks Key Pool + Pool-Proxy |
| [SINator-heypiggy](https://github.com/SIN-Rotator/SINator-heypiggy) | `:8002` | HeyPiggy Account Generator |
| [SINator-dashboard](https://github.com/SIN-Rotator/SINator-dashboard) | `:3000` | Tauri App (Provider-Switcher) |

```bash
# Alles starten (from dashboard repo):
cd ~/dev/SINator-dashboard && ./start.sh
```

---

## Client Konfiguration

### Quick Install (One-Liner)

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash
```

Mit API Key:
```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_xxx
```

### Manuelle Konfiguration

**OpenCode (`~/.config/opencode/opencode.json`):**
```json
{
  "provider": {
    "fireworks-ai": {
      "options": {
        "baseURL": "https://sinatorpool-router.delqhi.com/inference/v1",
        "apiKey": "<DEIN_API_KEY>"
      }
    }
  }
}
```

**Hermes (`~/.hermes/config.yaml`):**
```yaml
custom_providers:
  - name: fireworks
    base_url: https://sinatorpool-router.delqhi.com/inference/v1
    key_env: FIREWORKS_AI_API_KEY
```

**Python:**
```python
from openai import OpenAI
client = OpenAI(
    base_url="https://sinatorpool-router.delqhi.com/inference/v1",
    api_key="<DEIN_API_KEY>",
)
# List models (via Pool-Proxy /v1/models)
models = client.models.list()
```

**curl:**
```bash
curl https://sinatorpool-router.delqhi.com/inference/v1/models \
  -H "Authorization: Bearer <DEIN_API_KEY>"
```

---

## Was der Installer macht

1. **Pool Router Config** — `~/.hermes/config.yaml` mit `sinatorpool-router.delqhi.com`
2. **Pool Router Daemon** — `pool-router.py` via launchd `com.sinator.pool-router`
3. **10 Proxy Daemons** — `com.sinator.pool-proxy-{8888..8897}` via launchd
4. **412 Retry Patch** — `error_classifier.py`: 412 + "suspended" -> `billing` + retryable
5. **UA-Spoof Patch** — `_ua_patch.py` + `import _ua_patch` in `run_agent.py`
6. **Unlimited max_turns** — `999999` (kein Iterations-Limit)
7. **Model Discovery** — Pool-Proxy `/v1/models` Handler (Hermes `custom:*` provider)

## Management

```bash
# Router läuft?
pgrep -f pool-router.py

# Router stoppen
launchctl unload ~/Library/LaunchAgents/com.sinator.pool-router.plist

# Router starten
launchctl load ~/Library/LaunchAgents/com.sinator.pool-router.plist

# Proxys (alle 10)
launchctl list | grep pool-proxy

# Pool-Router Logs
tail -f /tmp/pool-router-launchd.log

# Einen Rotation-Durchlauf testen
python tools/rotate.py
```

## Struktur

```
├── agent_toolbox/
│   ├── core/
│   │   ├── gmx_service.py           # GMX Session + Alias-Rotation (Playwright-native)
│   │   ├── fireworks_service.py     # Fireworks Signup/Login/API-Key (Playwright+CUA)
│   │   ├── pool_manager.py          # API-Key Pool-Manager (Lease/Return/Stats)
│   │   ├── config_manager.py        # GMX+FW Credentials (data/config.json)
│   │   └── cua_helper.py            # CUA Window Detection (Onboarding only)
│   └── api/
│       └── routes/
│           ├── config.py              # GET/POST /api/v1/config
│           ├── pool.py                # Pool-CRUD + Stats
│           └── gmx.py                 # GMX Alias API
├── proxy/
│   ├── server.py                    # Pool-Proxy + /v1/models Handler
│   └── start-multi.sh               # 10 Proxys + Router starten
├── tools/
│   ├── install.sh                 # One-Command Installer
│   ├── manage_services.sh         # launchd Service Manager
│   ├── rotate.py                  # E2E Rotation (GMX → Fireworks → API Key)
│   ├── batch_rotate.py            # Automatische Rotation (alle 90s)
│   ├── gmx_alias_tool.py          # GMX Alias CLI (read-only)
│   ├── start_tunnel.sh            # Cloudflare Tunnel Manager
│   └── test_fireworks_api.py      # API-Test
├── patches/                       # Hermes CLI Patches
├── docs/
├── tests/
├── data/
│   └── config.json                  # GMX+FW Credentials
└── README.md
```

## API Key Lifecycle

| Status | Reaktion im Proxy |
|--------|-------------------|
| 401/402/403 (Key tot) | `_swap_key("suspended")` — meldet Key als suspended an Pool-API |
| 412 (Precondition Failed) | `_swap_key_silent("precondition_failed")` — Key bleibt verfügbar |
| 429 (Rate Limited) | `_swap_key_silent("rate_limited")` — Key bleibt verfügbar |
| 5xx (Server Error) | Nächster Proxy versuchen |

---

*Stand: 2026-05-29 | 218 Keys | 10 Proxys + Pool-Router | Playwright-native | V14*

# SINator — Fireworks AI Key Pool

Automated GMX alias rotation → Fireworks AI account → API key pool.
OpenAI-compatible proxy with automatic key rotation on rate-limits.

<<<<<<< HEAD
**Backend Port:** `8000` | **Pool-Router:** `9998` | **Base URL:** `https://sinatorpool-router.delqhi.com/inference/v1`
=======
**Base URL:** `https://sinatorpool-router.delqhi.com/inference/v1`

**12 Modelle:** deepseek-v4-pro, deepseek-v4-flash, glm-5p1, glm-5p1-fast, kimi-k2p5, kimi-k2p6, kimi-k2p6-turbo, qwen3p6-plus, minimax-m2p5, minimax-m2p7, gpt-oss-120b, gpt-oss-20b — jedes mit off/low/medium/high/max Thinking-Varianten (nicht-reasoning Modelle: temperature 0, kein thinking).

**Auto-Failover:** 413/429/412/5xx → automatisch nächster Proxy. Du merkst nichts davon.
>>>>>>> 481410c (Update README + INSTALL: 12 models, correct limits, remove stale config/ references)

---

## EINE Base-URL — Pool-Router mit Auto-Failover

Der Pool-Router verteilt Requests automatisch auf 10 lokale Proxys (8888-8897), jeder mit eigenem API-Key aus dem Pool. Bei 413/429/412/5xx springt der Router zum nächsten Proxy.

| Zugriff | Base URL |
|---------|----------|
| **Alle Clients** | `https://sinatorpool-router.delqhi.com/inference/v1` |

### Auto-Failover

| Status | Reaktion |
|--------|----------|
| 413 Payload Too Large | Nächster Proxy |
| 429 Rate Limit | Nächster Proxy |
| 412 Account Suspended | Nächster Proxy |
| 500/502/503/504 Server Error | Nächster Proxy |
| Alle Pools gleicher Fehler | Status-Code durchreichen |
| Proxy 3 Fehler in 60s | Cooldown — 60s Pause |

---

## Quick Start

```bash
<<<<<<< HEAD
python3 agent_toolbox/start_toolbox.py   # Backend :8000
bash proxy/start-multi.sh                 # 10 Proxys + Pool-Router :9998
python3 tools/rotate.py                   # Ersten Key holen
```
=======
mkdir -p ~/.config/opencode
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json -o ~/.config/opencode/opencode.json
```

Danach `apiKey` in der Datei ersetzen (`fw_DEIN_KEY` → dein echter Key).

### OpenCode CLI (One-Liner)

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_DEIN_KEY
```

Schreibt `~/.config/opencode/opencode.json` — fügt Fireworks Provider + 12 Modelle hinzu. Bestehende Settings bleiben erhalten.

### Config kaputt? Repair

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash
```

Erkennt ob `opencode.json` broken JSON ist oder nur der Provider fehlt. Bewahrt alles was geht, fügt Fireworks Provider + alle 12 Modelle hinzu.
>>>>>>> 481410c (Update README + INSTALL: 12 models, correct limits, remove stale config/ references)

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
Playwright Browser Automation
  ↓ ONE Browser für gesamten Flow
GMX → Fireworks AI → API Key
```

**Services (macOS LaunchAgents):**

| Service | Port | Purpose |
|---------|------|---------|
| `com.sinator.backend` | :8000 | FastAPI Backend |
| `com.sinator.pool-router` | :9998 | Pool-Router mit Auto-Failover |
| `com.sinator.pool-proxy-{8888..8897}` | :8888-:8897 | 10× OpenAI-compatible proxies |
| `com.sinator.pages` | :8040 | Landing page |

---

## Rotation Flow (V15.4 — ONE Browser)

```bash
<<<<<<< HEAD
python3 tools/rotate.py
# → ONE Browser → Alias Rotation (~55s) → Signup → OTP (~12s) → Verify
# → Login + Onboarding (~25s) → API Key (~30s) → Pool
=======
opencode chat                                           # default: deepseek-v4-pro
opencode chat --model deepseek-v4-pro --variant high    # 64000 thinking tokens
opencode chat --model kimi-k2p6 --variant max            # 64000 thinking tokens + vision
opencode chat --model gpt-oss-120b                       # kein thinking, deterministisch
opencode chat --model glm-5p1 --variant off              # kein thinking
>>>>>>> 481410c (Update README + INSTALL: 12 models, correct limits, remove stale config/ references)
```

| Step | Time | Method |
|------|------|--------|
| GMX Login + Consent | ~22s | Playwright |
| GMX Alias Delete + Create | ~33s | Playwright iframe |
| Fireworks Signup | ~15s | Playwright |
| OTP (GMX Inbox) | ~12s | Playwright + CDP OOPIF |
| Verify + Login + Onboarding | ~25s | Playwright + CUA (names only) |
| API Key | ~30s | Playwright |
| **Total** | **~169s** | |

<<<<<<< HEAD
---
=======
| Variant | Thinking | Typisch für |
|---------|----------|-------------|
| `off` | disabled | Schnelle Antworten, kein Reasoning |
| `low` | 4000 tokens | Leichtes Reasoning |
| `medium` | 16000 tokens | Standard |
| `high` | 32000-64000 tokens | Komplexe Aufgaben |
| `max` | 64000-65536 tokens | Maximales Reasoning |
>>>>>>> 481410c (Update README + INSTALL: 12 models, correct limits, remove stale config/ references)

## Project Structure

<<<<<<< HEAD
=======
| Modell | ID | Thinking | Vision | Context |
|--------|----|----------|--------|---------|
| DeepSeek V4 Pro | `fireworks/deepseek-v4-pro` | 64000 | nein | 1M |
| DeepSeek V4 Flash | `accounts/fireworks/models/deepseek-v4-flash` | 32000 | nein | 1M |
| GLM 5.1 | `fireworks/glm-5p1` | 32000 | nein | 202K |
| GLM 5.1 Fast | `accounts/fireworks/routers/glm-5p1-fast` | 32000 | nein | 202K |
| Kimi K2.5 | `accounts/fireworks/models/kimi-k2p5` | 32000 | ja | 262K |
| Kimi K2.6 | `fireworks/kimi-k2p6` | 32000 | ja | 262K |
| Kimi K2.6 Turbo | `accounts/fireworks/routers/kimi-k2p6-turbo` | 32000 | ja | 262K |
| Qwen3.6 Plus | `accounts/fireworks/models/qwen3p6-plus` | 32000 | ja | 131K |
| MiniMax M2.5 | `accounts/fireworks/models/minimax-m2p5` | 32000 | nein | 196K |
| MiniMax M2.7 | `fireworks/minimax-m2p7` | 32000 | nein | 196K |
| GPT-OSS 120B | `accounts/fireworks/models/gpt-oss-120b` | — | nein | 131K |
| GPT-OSS 20B | `accounts/fireworks/models/gpt-oss-20b` | — | nein | 131K |

### Python / curl / beliebiger OpenAI-Client

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://sinatorpool-router.delqhi.com/inference/v1",
    api_key="fw_DEIN_KEY",
)
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Hallo"}],
)
>>>>>>> 481410c (Update README + INSTALL: 12 models, correct limits, remove stale config/ references)
```
agent_toolbox/
├── core/
│   ├── gmx_service.py         GMX Login, Alias, OTP (Playwright-native)
│   ├── fireworks_service.py    Fireworks Signup/Login/API-Key (Playwright+CUA)
│   ├── pool_manager.py         API-Key Pool-Manager (Lease/Return/Stats)
│   ├── keychain_store.py       macOS Keychain Encryption
│   ├── config_manager.py       GMX+FW Credentials (data/config.json)
│   ├── cua_helper.py           CUA Window Detection (Onboarding only)
│   └── cdp_client.py           Raw CDP WebSocket (OOPIF fallback)
├── api/routes/
│   ├── gmx.py                  GMX API Endpoints
│   ├── fireworks.py            Fireworks API Endpoints
│   ├── pool.py                 Pool-CRUD + Stats
│   ├── rotation.py             Full Rotation Orchestrator
│   ├── config.py               GET/POST /api/v1/config
│   └── schemas.py              Pydantic Models
├── static/dashboard.html       Dashboard SPA
└── start_toolbox.py            FastAPI Entry Point

proxy/
├── server.py                   Pool-Proxy (aiohttp SSE, auto-swap)
├── pool_client.py              Backend API Client
├── key_cache.py                Key Pre-fetch Cache
├── config.py                   Proxy Configuration
└── start-multi.sh              Startet Pool-Router + 10 Proxys

scripts/
├── pool-router.py              Pool-Router (ThreadingMixIn)
└── pool-router.plist           LaunchAgent

tools/
├── rotate.py                   V8: ONE Browser Rotation (main entry)
├── batch_rotate.py             Batch N Rotations
├── gmx_alias_tool.py          GMX Alias CLI
├── open_gmx_email.py          GMX Email Opener
├── swap_key.py                Key Swap CLI
├── install.sh                 Service Installer
├── manage_services.sh         Service Management
└── autostart.sh               Autostart Script
```

---

## Known Issues

<<<<<<< HEAD
| Issue | Workaround |
|-------|------------|
| Fireworks $5 Credits aufgebraucht = Suspension | Key als `used` markieren |
| OTP-Email kann bis zu 180s dauern | 25×8s Polling, Fallback: `partial` |
| GMX Alias Create scheitert intermittierend | Retry in rotate.py (3 Versuche) |
| `connect_over_cdp()` hängt mit Chrome 148 | `chromium.launch()` statt `connect_over_cdp()` |
| Cookie-Injection verursacht `logoutlounge` | Frischer Browser ohne Cookies |
=======
| Datei | Zweck |
|-------|-------|
| `opencode.json` | Provider-Konfiguration (Single Source of Truth) |
| `opencode-config-install.sh` | One-Liner Installer für OpenCode CLI |
| `opencode-config-repair.sh` | Emergency Repair für broken `opencode.json` |
| `INSTALL.md` | Detaillierte Install-Optionen + Troubleshooting |
| `tests/test_opencode_config.py` | Test-Suite (19 Tests) |
>>>>>>> 481410c (Update README + INSTALL: 12 models, correct limits, remove stale config/ references)

---

*Stand: 2026-05-31 | 235 Keys | Pool-Router: sinatorpool-router.delqhi.com | V15.4 ONE Browser*

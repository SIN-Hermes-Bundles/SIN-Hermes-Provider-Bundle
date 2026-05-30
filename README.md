# SINator — Fireworks AI Key Pool

Automated GMX alias rotation → Fireworks AI account → API key pool.
OpenAI-compatible proxy with automatic key rotation on rate-limits.

**Backend Port:** `8000` | **Pool-Router:** `9998` | **Base URL:** `https://sinatorpool-router.delqhi.com/inference/v1`

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
python3 agent_toolbox/start_toolbox.py   # Backend :8000
bash proxy/start-multi.sh                 # 10 Proxys + Pool-Router :9998
python3 tools/rotate.py                   # Ersten Key holen
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
python3 tools/rotate.py
# → ONE Browser → Alias Rotation (~55s) → Signup → OTP (~12s) → Verify
# → Login + Onboarding (~25s) → API Key (~30s) → Pool
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

---

## Project Structure

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

| Issue | Workaround |
|-------|------------|
| Fireworks $5 Credits aufgebraucht = Suspension | Key als `used` markieren |
| OTP-Email kann bis zu 180s dauern | 25×8s Polling, Fallback: `partial` |
| GMX Alias Create scheitert intermittierend | Retry in rotate.py (3 Versuche) |
| `connect_over_cdp()` hängt mit Chrome 148 | `chromium.launch()` statt `connect_over_cdp()` |
| Cookie-Injection verursacht `logoutlounge` | Frischer Browser ohne Cookies |

---

*Stand: 2026-05-31 | 235 Keys | Pool-Router: sinatorpool-router.delqhi.com | V15.4 ONE Browser*

# BUILDING PLAN — SINator Fireworks AI V12 ✅ (2026-05-26)

## ✅ V12 Status: COMPLETE

```
GMX Login (built-in, Step 0) → Alias Rotation (~180s) → Fireworks Signup
→ OTP → Verify → Login → Onboarding → Playwright Fallback → API Key → Pool
Pool: 225 Keys (20 verfügbar, 11 used, 194 suspended)
Cycle Time: ~140s avg
Pool-Router: :9998 (ThreadingMixIn) → 10 Proxys :8888-:8897
Pool-Router URL: sinatorpool-router.delqhi.com (single endpoint, auto-failover)
API Key (alle Macs): <DEIN_API_KEY>
Dashboard SSE live
```

| Flow | Name | Status | Tool |
|------|------|:---:|------|
| #0 | GMX Session | ✅ | Playwright "Zum Postfach" click → SID |
| #1 | GMX Alias Delete | ✅ | New-Tab allEmailAddresses URL → hover+click+OK |
| #1 | GMX Alias Create | ✅ | New-Tab allEmailAddresses URL → fill+click, verify empty |
| #2 | Fireworks Signup | ✅ | Playwright + CUA: email→pw→Create→OTP→Verify |
| #3 | Fireworks Login | ✅ | Playwright form `a:has-text("Email Login")` + CUA onboarding |
| #4 | Onboarding | ✅ | CUA: "First"+"Last" type_text + Terms AXPress + Playwright Fallback |
| #5 | Use-Case + $5 | ✅ | CUA dynamic scan text-based checkboxes |
| #6 | API Key | ✅ | PopUpButton force-click + menuitem + Generate (disabled-wait + polling) |
| #7 | Pool | ✅ | Auto-save to keychain (146 keys total) |

## ✅ V12 Changes (2026-05-26)

### 3 Pool-Proxies + Tunnel Subdomains
- Pool-Router (`:9998`) mit ThreadingMixIn + 10 Proxy-Instanzen (`:8888`-`:8897`)
- EINE baseURL: `sinatorpool-router.delqhi.com` (Auto-Failover über alle Proxys)
- `proxy/start-multi.sh` startet alle 3 + killt alte Instanzen
- Kein Backup-Key mehr (`SIN_NO_BACKUP=true`)

### GMX Navigation V12 — Playwright Shadow DOM
- CUA `find_cua_window` funktioniert nicht mehr (Chrome-Tab-Titel leer bei programmatischen Tabs)
- Reiner Playwright-Ansatz: `ACCOUNT-AVATAR-NAVIGATOR` → JS `.click()` + `dispatchEvent(mouseenter)` → Shadow DOM traversal → "E-Mail Einstellungen"
- Settings-Seite lädt `signature/settings` iframe → "E-Mail-Adressen" klicken → `allEmailAddresses` iframe
- 20×1s Polling bis iframe gefunden

### Double-Key-Waste Fix (Atomic Report+Lease)
- `pool_manager.report_key()` leaset Ersatz-Key jetzt **atomar** (im gleichen Lock wie suspend)
- Proxy nutzt `report()`-Result direkt — kein extra `lease()`
- Backend: `report_key(api_key, key_id, reason, leased_to, ttl_seconds)`
- Proxy: `_swap_key()` prüft `report_result.get("new_key")` → nutzt direkt

### 429 Handling — Client Return statt Intern Retry
- Transientes 429 → Proxy gibt SOFORT 429 an Client zurück mit `Retry-After` Header
- Kein internes Warten mehr (verhindert Client-Timeouts + InvalidHTTPResponse)

### Chrome Tab Cleanup
- Nach 4h Batch-Rotation → 37 Tabs offen → Chrome überlastet → `connect_over_cdp` Timeout
- `rotate.py` schließt jetzt ALLE non-essential Tabs (nicht nur GMX/Fireworks)
- Nur Dashboard + 1 GMX-Inbox bleiben

### CDP Target Selection — Inbox bevorzugen
- `get_page_target()` priorisiert `navigator.gmx.net` URLs über `www.gmx.net`
- Homepage hat keinen "Einstellungen"-Button

### Config Manager — GMX + Fireworks Credentials
- `agent_toolbox/core/config_manager.py` — speichert `gmx_email`, `gmx_password`, `fireworks_password` in `data/config.json`
- `agent_toolbox/api/routes/config.py` — `GET /api/v1/config` + `POST /api/v1/config` (public, kein Auth)
- Rotation nutzt `get_config()` → `--gmx-email` + `--gmx-password` + `--password` (nicht mehr hardcodiert!)
- Setup-Seite `/setup` im Dashboard — Formular für alle Credentials + 3 Pool-URLs + API Key

### Pool-Stats: `leased` entfernt
- `available = total - used - suspended` (geleastete Keys zählen als verfügbar)
- Dashboard zeigt: Gesamt / Verfügbar / Verbraucht

### Chat-Assistent (Dashboard /hilfe)
- Rust-Command `chat_send` ruft Pool-Proxy (`localhost:8888`) auf
- Modell: `accounts/fireworks/models/gpt-oss-120b` ($0.15/M input)
- System-Prompt in `src-tauri/chat-system-prompt.txt` (include_str!)
- Live-Pool-Stats + Backend-Health in Rust geholt → in System-Prompt injiziert

### Pool-Verschlüsselung
- 146/146 API-Keys in macOS Keychain (`com.sinator.pool`)
- `keychain_store.py` mit CRUD + Migration
- `GET /pool/reveal/{key_id}` hydratisiert Key aus Keychain
- Pool-JSON enthält nur SENTINEL-Werte (keine Keys im Klartext)

### CORS + Auth
- `/api/v1/config` in `public_prefixes` (kein Auth-Token nötig)
- CORS Origins: `https://tauri.localhost`, `tauri://localhost`, `http://localhost:3000`, `http://localhost:8000`

---

## ✅ V5-V12 Completed Milestones

| # | Task | Ergebnis |
|---|------|----------|
| 1 | Full-Flow Automation | `rotation.py` V12 — Playwright+CUA+CDP hybrid |
| 2 | API-Key Pool | 146 Keys (59 available), auto-save + Keychain |
| 3 | fireworks_service.py | 3103→114 Zeilen (-96%), V5 Playwright+CUA |
| 4 | V5 Cleanup | Obsolete files gelöscht (preflight.py, command_registry.json, etc.) |
| 5 | Single Command | `python tools/rotate.py` — E2E in einem Befehl |
| 6 | Dynamic CUA Scanning | Text-based `_find_element()` — keine Hardcoded-Indizes |
| 7 | Chrome Config | NON-accessibility mode: `--profile-directory="Profile 901"`, Port 9222 |
| 8 | V7 Self-Healing | Rate-Limit Backoff, OOPIF Polling, API Key Retry |
| 9 | V8 GMX Nav Fix | Playwright inbox goto + CUA Einstellungen + JS hidden-nav + New-Tab iframe |
| 10 | V9 Sleep-Reduktion + Bugfixes | health mark_used(), Dashboard override, PoolManager reload |
| 11 | V10 CUA PID Targeting | lsof PID-Ermittlung, target_pid an find_cua_window |
| 12 | V11 Config Manager + Chat + Keychain | Credentials API, Rust chat_send, Keychain encryption |
| 13 | V13 Pool-Router | EINE baseURL, 10 Proxys, ThreadingMixIn, silent swap |

---

## 📌 PROJECT COMPLETE — Maintenance Mode

**Keine neuen Features mehr.** V12 = letzte geplante Version.
Ab jetzt nur noch:

| Aktivität | Beschreibung |
|-----------|-------------|
| 🐛 Bugfixes | Wenn was im Live-Betrieb kaputt geht |
| 🔄 Live Runs | `python tools/rotate.py` — Keys generieren |
| 📝 AGENTS.md | Learnings aus Live-Runs dokumentieren |

**Status:** Feature-Complete ✅ — 225 Keys, ~140s/Rotation, Pool-Router + 10 Proxys, Config Manager, Keychain, Chat-Assistent, Session Reuse.

---

## 📌 Known Issues

### Account Suspension
Fireworks suspendiert Accounts bei Spending Limit ($5 Credits aufgebraucht):
```
Account golden-cobra-560-66c is suspended, possibly due to reaching the monthly
spending limit or failure to pay past invoices.
```
**Workaround:** Key via `POST /pool/report` als suspended markieren → Proxy holt atomar Ersatz-Key.

### 429 Rate Limiting
Transientes 429 bei hoher Last → Proxy gibt SOFORT 429 an Client zurück mit `Retry-After: 5s`.
Kein internes Retry mehr (verhindert Timeouts).

### Chrome Tab Overload
Nach 4h Batch-Rotation → 37+ Tabs → Chrome überlastet.
**Workaround:** `rotate.py` räumt jetzt ALLE non-essential Tabs auf (nur Dashboard + 1 GMX-Inbox bleiben).

---

## 🚀 Quick Start (V11)

```bash
# Chrome mit Profile 901 (OHNE accessibility!)
nohup "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir="/Users/jeremy/Library/Application Support/Google Chrome" \
  --profile-directory="Profile 901" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  > /tmp/chrome_sinator.log 2>&1 &

# CUA Daemon
cua-driver serve &

# Full Rotation (Single Command — liest Config aus data/config.json)
python tools/rotate.py

# API Server
python agent_toolbox/start_toolbox.py

# Pool Stats
curl -s http://localhost:8000/pool/stats | python3 -m json.tool

# Config setzen (GMX + FW Credentials)
curl -X POST http://localhost:8000/api/v1/config \
  -H 'Content-Type: application/json' \
  -d '{"gmx_email":"opensin@gmx.de","gmx_password":"ZOE.jerry2024","fireworks_password":"ZOE.jerry2024!"}'
```

---

## 🏗️ Services (LaunchAgents)

| Service | Port | Beschreibung |
|---------|------|-------------|
| `com.sinator.backend` | :8000 | FastAPI Backend |
| `com.sinator.pool-proxy-{8888..8897}` | :8888-:8897 | 10× aiohttp SSE + silent swap Proxies |
| `com.sinator.pool-router` | :9998 | Pool-Router mit ThreadingMixIn + Failover |
| `com.sinator.pages` | :8040 | Landing Page |
| `com.sinator.chrome` | :9222 | Chrome mit Profile 901 |
| `com.sinator.cua-driver` | — | CUA AX-Daemon |

### Pool-Router-Routing
- `/` → `:8040` (Landing Page)
- `/inference/v1/*`, `/v1/*` → Pool-Router :9998 → 10 Proxys :8888-:8897
- `/api/*`, `/docs` → :8000 (Backend)

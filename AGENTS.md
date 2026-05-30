# AGENTS.md — SINator Fireworks AI Rotator V15.2 (2026-05-30)

## ✅ COMPLETE E2E FLOW — VERIFIED 2026-05-30

```bash
python tools/rotate.py
# → GMX Login (Step 0) → Alias Rotation (~27s) → Fireworks Signup
# → OTP (~11s, Playwright locator) → Verify → Login → Onboarding → API Key → Pool
```

**Pool:** 225 Keys (avail/used/suspended)
**Cycle Time:** ~27s GMX + ~60s Fireworks signup + ~30s API Key = ~140s total
**Pool-Router:** `sinatorpool-router.delqhi.com` (:9998, single endpoint, auto-failover)
**Pool Proxies:** 10 Instanzen (:8888-:8897) hinter Pool-Router
**Services:** com.sinator.backend (:8000), com.sinator.pool-router (:9998), 10× pool-proxy (:8888-:8897), Pages (:8040)

---

## 🔧 V15.3 CHANGES (2026-05-30) — `connect_over_cdp → launch()` (Chrome 148 Fix)

### Problem: `connect_over_cdp` hängt mit Chrome 148
Playwright `connect_over_cdp()` zu Chrome 148.0.7778.215 timeoutet nach 180s (Protocol-Mismatch). Ursache: Playwright 1.58.0/1.60.0 Node.js-Driver unterstützt CDP-Protokoll von Chrome 148 nicht.

### Fix: `chromium.launch()` statt `connect_over_cdp`
Alle 4 Funktionen (gmx + fireworks) nutzen jetzt `chromium.launch()` mit FRISCHEM Browser:
- **gmx_service.py** `_pw_connect()`: `p.chromium.launch(headless=False)` statt `connect_over_cdp()`
- **fireworks_service.py** `signup_fireworks()`, `login_fireworks()`, `create_api_key()`, `verify_account()`: gleicher Fix
- `_pw_close()` für saubere Ressourcen-Freigabe (finally-Block in `rotate_alias()`)

### Keine Cookie-Injection mehr
- Vorher: `context.add_cookies()` aus `data/gmx-cookies.json` → injizierte `__Host-ls.keep_me_signed_in` → GMX redirectet zu `logoutlounge?status=session` (Cookie-Session abgelaufen)
- Jetzt: FRISCHER Browser ohne Cookies → Konsent-Handler → voller Email+Password Login auf `auth.gmx.net`. **Kein CAPTCHA.** (GMX zeigt CAPTCHA nur bei verdächtigen IPs/Browsern, Playwright Chromium ist vertrauenswürdig.)

### Consent-Handler Fix
- GMX Consent-Portal lädt in Cross-Origin iframe (`plus.gmx.net/lt`). Button `#save-all-pur` ist darin.
- `page.locator('#save-all-pur')` findet NICHTS (sucht nur main frame).
- Fix: `for frame in page.frames: frame.locator('#save-all-pur')` — iteriert ALLE Frames.
- 77 GMX-Cookies werden nicht mehr injiziert (verursachten `logoutlounge`).

### Neue Messwerte
- **GMX Alias Rotation**: ~52s (davon ~22s Login + Consent)
- **Gesamt-Zyklus**: ~52s GMX + ~60s Fireworks signup + ~30s API Key = ~140s (unverändert)
- **Keine Abhängigkeit von laufendem Chrome 148** — funktioniert auch wenn Chrome geschlossen ist

---

## 🔧 V15.2 CHANGES (2026-05-30) — Session Expiry Auto-Recovery + Dashboard Terminal Launch

### Session Expiry Auto-Recovery (gmx_service.py:380-410)
**Problem:** GMX SID läuft ab → `navigator.gmx.net/.../mail_settings?sid=...` redirectet zu `www.gmx.net/?status=inactive` oder `logoutlounge?status=session`
**Fix:** `_navigate_to_all_email_addresses()` erkennt `status=inactive` / `logoutlounge` im Jump-Result → triggert `_login()` via `keep_me_signed_in` Cookie (gültig bis 2026-11) → holt frischen SID → retry Jump. Kein CAPTCHA nötig.

### Dashboard: Generieren-Button → Terminal.app
**Alt:** `POST /api/v1/rotation/full` (Subprocess → Playwright CDP Timeout, funktionierte nie zuverlässig)
**Neu:** Tauri-Command `open_terminal_rotate(password, count)` in Rust → öffnet Terminal.app via osascript → führt `python3 tools/rotate.py` direkt aus. Key landet via `--save` im Pool.
**Escaping:** Single-Quotes in Shell, `"` → `\"` in AppleScript. KEIN `\` escapen (Doppel-Escaping-Bug).

---

## 🔧 V15 CHANGES (2026-05-30) — Playwright locator + CUA-Restriction

### CUA: KEINE Web-Content-Interaktion mehr
**Erkannt:** `cua_get_window_state()` liefert Chrome-AX-Tree (Tabs, Bookmarks, Browser-UI), **nicht** Web-Content. Checkboxen/Buttons sind darin nicht sichtbar.

**Fix in `login_fireworks()`:**
- CUA nur für `AXTextField` (Name-Felder) via `_cua_type()` — das funktioniert, weil Chrome Text-Felder im AX-Tree exponiert
- Checkbox/Continue/Submit/Use-Cases komplett via Playwright `_fireworks_playwright_onboarding()`
- Bei fehlendem CUA-Window: Playwright type() als Fallback für Names

### _fireworks_playwright_onboarding() — Checkbox-Fix (Radix UI)
**Problem:** Terms-Checkbox ist ein Radix UI `<button role="checkbox">`, NICHT `<input type="checkbox">`. `label:has-text("Terms")` matched den "Terms of Service" Link. Playwright `click()` und `dispatchEvent` toggeln den State entweder gar nicht oder sofort zurück.
**Fix:** `button[role="checkbox"]` via `page.locator()` finden, dann native `el.click()` ausführen (`await btn.evaluate('el => el.click()')`). Das triggert den React/Radix State-Change und rendert das SVG-Icon. Chrome Password Save Dialog vorher dismissen.

### read_otp() — Playwright locator statt JS Walk
**Problem:** `document.querySelectorAll()` findet NUR 74 light-DOM Elemente. GMX `list-mail-item` sind in >2 Ebenen Shadow DOM, unsichtbar für native DOM-APIs.
**Fix:** `webmailer_frame.locator('list-mail-item.list-mail-item--unread').filter(has_text='fireworks').first.click()` — Playwright locator durchdringt Shadow Boundaries nativ.

### gmx_service.py — Playwright-native (1034 Zeilen)

**Aktualisiert:**
- `_find_alias_row()` — Nutzt jetzt `div.table_body-row` statt `document.body.innerText` — findet Aliases zuverlässiger in tabellarischer Struktur
- `_delete_alias()` — `div.table_body-row:has-text()` für Row-Selektion, Dialog-Handler vor Click, JS dispatchEvent Fallback, DOM-Dialog Bestätigung (Löschen/OK/Bestätigen/Ja/Entfernen), Verifikation via table rows statt body.innerText
- `_verify_alias()` — Prüft `div.table_body-row` statt `document.body.innerText` für zuverlässigere Präsenz/Absenz-Prüfung
- `read_otp()` Z.860-884: JS Walk durch Playwright locator ersetzt (findet 42 list-mail-items vs. 0 via querySelectorAll)
- `open_gmx_email()` Z.951-973: gleicher Fix
- `open_gmx_email()` Z.977: `result`→`clicked` (stale Variable)

### 🔧 V15.1 CHANGES (2026-05-30) — Session Reuse + Use-Cases Fix

**Problem 1: Use-Cases Checkboxen nicht gesetzt**
- `input[type="checkbox"]` mit `aria-label` Matching funktionierte NICHT — Checkboxen wurden nicht gesetzt
- **Fix:** `label:has-text("{use_case}")` als primäre Strategie (wie im alten Code von letzter Woche). Click auf Label triggert den echten Input. Fallback: `input[type="checkbox"]` mit `aria-label`.

**Problem 2: Continue/Next Button nicht zuverlässig gefunden**
- Nur ein einfacher Button-Scan traf manchmal den falschen Button
- **Fix:** 3 Strategien: 1) `button:has-text("Continue")` + `is_visible() + not is_disabled()`, 2) `button[type="submit"]`, 3) Case-insensitive Scan aller Buttons. 2s wait nach Terms-Checkbox für React re-render.

**Problem 3: API Key Seite redirected zu /login**
- `create_api_key()` erstellte eine neue Page, aber Session-Cookies waren nicht gültig für API Key Seite
- **Fix:** `login_fireworks()` gibt jetzt `page`, `playwright`, `browser` zurück. `create_api_key()` akzeptiert diese optional und wiederverwendet die Session. `rotate.py` übergibt sie durch.
- **Impact:** Neue Signatur: `create_api_key(key_name, page=None, playwright=None, browser=None)`

**Problem 4: Indentation Chaos in `create_api_key()`**
- Durch viele inkrementelle Edits war die Funktion komplett durcheinandergeschrieben
- **Fix:** `create_api_key()` komplett neu aufgebaut mit korrekter Indentation

**Verification:**
```
✅ GMX Alias: spectra-shark-157@gmx.de (20.55s)
✅ Fireworks Signup: Account verified
✅ Login + Onboarding: Redirect to /account/home
✅ API Key: fw_VXv4hCMCa9VWbVcidTdqD
✅ Pool: 225 Keys total

🎉 ROTATION COMPLETE — 139.6s
```

---

## 🔧 V14 CHANGES (2026-05-29) — Playwright-native Migration

### fireworks_service.py — V6 Restored (Playwright+CUA Hybrid)
**Vorher:** 3103 Zeilen CDP-only (V5), dann 216 Zeilen CDP-only (V7), dann broken
**Jetzt:** 655 Zeilen — bewährter V6 Code (Playwright + CUA Hybrid)

**Funktionen:**
- `signup_fireworks(email, password)` — Signup + OTP + Verify
- `login_fireworks(email, password)` — Login + Onboarding (CUA + Playwright Fallback)
- `create_api_key(key_name, page=None, playwright=None, browser=None)` — API Key erstellen via Playwright (Session Reuse)
- `verify_account(verify_url)` — Verify URL öffnen
- `_fireworks_playwright_onboarding(page)` — Playwright-Onboarding-Fallback
- `_generate_and_poll_key(pg, key_name)` — Generate-Button + Key-Polling

**OTP Polling:** 25 Versuche × 8s = 200s max. Fallback: `partial` status wenn OTP nicht kommt (Account ist unverified aber oft loginbar).

### rotate.py — V7 Playwright-native (108 Zeilen)
**Vorher:** 157 Zeilen mit CDP-Login, Onboarding, API Key (alles CDP)
**Jetzt:** 108 Zeilen — nutzt nur `fireworks_service.py` Funktionen

```python
# rotate.py flow:
1. GmxService.login() → Playwright
2. GmxService.rotate_alias() → Playwright
3. signup_fireworks(alias, password) → Playwright
4. login_result = login_fireworks(alias, password) → Playwright + CUA (gibt page+playwright+browser zurück)
5. create_api_key(key_name, page=login_result['page'], playwright=login_result['playwright'], browser=login_result['browser']) → Playwright (Session Reuse)
6. PoolManager.add_key() → JSON
```

**Kein CDP mehr im rotate.py!** Alles über Playwright-API-Calls. Session Reuse zwischen Login und API Key.

### gmx_service.py — Playwright-native (910 Zeilen)
**Vorher:** Mix aus CDP + CUA + Playwright
**Jetzt:** Playwright-native für alle Operationen

- `_navigate_to_all_email_addresses()` — Playwright shadow DOM traversal
- `_login()` — Playwright form fill
- `_delete_alias()` — Playwright iframe interaction
- `_create_alias()` — Playwright iframe interaction
- `read_otp()` — CDP-basiert (MailCheck Extension + OOPIF), unverändert — bewährt

---

## 🔧 V13 CHANGES (2026-05-29) — Fireworks Model Discovery

### Pool-Proxy `/v1/models` Handler
- `proxy/server.py` — `_handle_v1_models()` liest `~/.hermes/models_dev_cache.json`
- Gibt ALLE Fireworks Modelle + Router zurück (12 aktuell)
- Routen: `/v1/models` + `/inference/v1/models` (vor Catch-All registriert)
- `PUBLIC_PROXY_PATHS` um `/v1/models` erweitert

### Hermes `custom:*` Provider Support
- `patches/hermes_cli/models.py` — `provider_model_ids()` behandelt `custom:` prefix
- Probt `/v1/models` live über Pool-Proxy
- Model-Picker zeigt Fireworks-Modelle (vorher: 0, jetzt: 12)

---

## 🔧 V12 CHANGES (2026-05-26)

### Config Manager — GMX + Fireworks Credentials
- `agent_toolbox/core/config_manager.py` — speichert in `data/config.json`
- API: `GET /api/v1/config` + `POST /api/v1/config` (public, kein Auth)
- `rotate.py` liest Config → übergibt `--gmx-email` + `--gmx-password` + `--password`

### Setup-Seite (Dashboard)
- `/setup` — Formular für GMX Email, GMX Passwort, Fireworks Passwort
- Show/Hide Toggle auf Passwort-Feldern

### Pool-Stats: `leased` entfernt
- `available = total - used - suspended`
- `leased` Feld entfernt aus Schema, Route, Pool Manager

### Chat-Assistent (Dashboard /hilfe)
- Rust-Command `chat_send` → Pool-Router (`localhost:9998`)
- Modell: `accounts/fireworks/models/gpt-oss-120b` ($0.15/M input)
- System-Prompt in `src-tauri/chat-system-prompt.txt`
- Live-Pool-Stats + Backend-Health im System-Prompt

### CORS + Auth
- `/api/v1/config` zu `public_prefixes` hinzugefügt
- CORS Origins: `https://tauri.localhost`, `tauri://localhost`, `http://localhost:3000`, `http://localhost:8000`

### Tauri Build
- Neue Dependencies: `reqwest`, `tokio`, `futures-util`
- `chat_send` Command registriert

---

## 🔧 V12 FIXES (2026-05-26)

### Pool-Router + 10 Proxys
- EIN Pool-Router (:9998) verteilt auf 10 Proxy-Instanzen (:8888-:8897)
- Auto-Failover bei 413/429/412/5xx
- Cooldown nach 3 Fehlern (60s Pause)
- Start: `proxy/start-multi.sh`

### GMX Navigation — Playwright Shadow DOM
- Reiner Playwright-Ansatz — kein CUA für Navigation
- `ACCOUNT-AVATAR-NAVIGATOR` Custom Element → JS `.click()` + `dispatchEvent(mouseenter)`
- Shadow DOM traversal → "E-Mail Einstellungen" → settings iframe → "E-Mail-Adressen"
- `3c.gmx.net` (HTTPS, direkt) funktioniert für direkte Navigation

### Double-Key-Waste Fix (Atomic Report+Lease)
- `pool_manager.report_key()` leaset Ersatz-Key atomar (im gleichen Lock wie suspend)
- Proxy `_swap_key()` nutzt `report()`-Result direkt — kein extra `lease()`

### 429 Handling — Client Return
- Transientes 429 → SOFORT an Client zurück mit `Retry-After` Header
- Kein internes Warten mehr

### Chrome Tab Cleanup
- `rotate.py` schließt ALLE non-essential Tabs nach jeder Rotation
- Nur Dashboard + 1 GMX-Inbox bleiben

### CDP Target Selection — Inbox bevorzugen
- `get_page_target()` priorisiert `navigator.gmx.net` über `www.gmx.net`

---

## 🐛 BEKANNTE PROBLEME

### Fireworks Account Suspension (Spending Limit)
```
Account golden-cobra-560-66c is suspended, possibly due to reaching the monthly
spending limit or failure to pay past invoices.
```
- Jeder FW Account hat $5 Credits — sobald aufgebraucht = Suspension
- Betroffene Keys müssen als `used` markiert werden
- Workaround: `POST /pool/report` oder `POST /pool/use` für suspended Keys

### OTP-Email Verzögerung
- Fireworks Verify-Email kann bis zu 180s brauchen
- Fix: 25×8s = 200s Polling in `signup_fireworks()`
- Fallback: `partial` status — Account ist unverified aber oft loginbar

### Unverified Account = API Key Blocked
- Account erstellt, aber unverified → API Key Seite redirected zu `/login`
- Fix: Verify-URL muss geöffnet werden (oder Account ist verified)
- Workaround: Nach `partial` signup → `login_fireworks()` versucht trotzdem

---

## 🔑 CRITICAL PATTERNS (MANDATORY)

### `_pw_connect()` — `chromium.launch()` statt `connect_over_cdp()`
- **NICHT** `connect_over_cdp()` verwenden (hängt mit Chrome 148 — Protocol-Mismatch)
- **IMMER** `chromium.launch(headless=False)` — frischer Browser, kein CAPTCHA
- `_pw_close()` im finally-Block aufrufen (Browser-Ressourcen freigeben)
- Kein Cookie-Injection `context.add_cookies()` — verursacht `logoutlounge`-Redirect
- Consent-Handler: `for frame in page.frames: frame.locator('#save-all-pur')` — Cross-Origin iframe

### Playwright Form Interaction
```python
# Email/Password
page.locator('input[name="email"]').first.fill(email)
page.locator('input[name="password"]').first.fill(password)

# Button matching via text content
for btn in await page.locator('button[type="submit"]').all():
    if 'Next' in (await btn.text_content() or ''):
        await btn.click(force=True); break

# API Key (Playwright) — disabled-Wait + DOM-Polling
for _ in range(15):
    for btn in await page.locator('button').all():
        txt = (await btn.text_content() or '').strip()
        if 'Generate' == txt and not await btn.is_disabled():
            await btn.click(force=True); break
```

### GMX Alias Delete (Playwright iframe)
```python
frame = [f for f in page.frames if 'allEmailAddresses' in f.url][0]
frame.locator(f'text={alias_email}').first.hover()
frame.locator('[title*="löschen"]').first.click(force=True)
```

### GMX Alias Create (Playwright iframe)
```python
inp = frame.locator('input[type="text"]').first
await inp.fill("name-123")
btn = frame.locator('button:has-text("Hinzufügen")').first
await btn.click(force=True)
# verify: inp.input_value() == '' = success
```

### CUA Onboarding (NUR für Name-Textfelder)
```python
# Names: "First" + "Last" suchen, NICHT "Name"
el = _find_element("First", "AXTextField")  # richtig
# el = _find_element("Name", "AXTextField")  # FALSCH!

# Rest via Playwright (CUA kann nur AXTextField — Chrome UI, nicht Web-Content)
await _fireworks_playwright_onboarding(page)
```

### OTP Polling (read_otp)
```python
# Find first unread Fireworks email via Playwright locator (pierces shadow DOM!)
items = webmailer_frame.locator('list-mail-item.list-mail-item--unread').filter(has_text='fireworks')
if await items.count() > 0:
    await items.first.click()
# OOPIF erscheint automatisch → CDP attach_to_iframe + regex URL extraction
```

---

## 📁 ARCHITECTURE

```
agent_toolbox/
├── core/
│   ├── fireworks_service.py    V6: Playwright+CUA Hybrid + launch() (682 lines)
│   ├── gmx_service.py          Playwright-native, launch() statt connect_over_cdp (1071 lines)
│   ├── pool_manager.py         Pool-Stats + Key-Management (518 lines)
│   ├── config_manager.py       GMX+FW Credentials (46 lines)
│   └── cua_helper.py           CUA Window Detection (nur für Onboarding)
├── api/
│   └── routes/
│       ├── config.py           GET/POST /api/v1/config
│       ├── pool.py             Pool-CRUD + Stats
│       └── gmx.py              GMX Alias API
└── start_toolbox.py            FastAPI entry point

proxy/
├── server.py                   Pool-Proxy (596 lines) + /v1/models Handler
└── start-multi.sh              Startet Pool-Router + 10 Proxys

tools/
├── rotate.py                   V7: Playwright-native + Session Reuse (108 lines)
├── gmx_alias_tool.py          GMX Alias CLI (read-only verified)
└── test_fireworks_api.py      API-Test

Dashboard (Tauri):
src-tauri/src/
├── main.rs                     chat_send Command (reqwest → Pool-Proxy)
└── chat-system-prompt.txt      System-Prompt für Chat-Assistent
```

---

## 🔗 CROSS-REFERENCES — SINator Ecosystem

| Repo | Port | Was |
|------|------|-----|
| **SINator-fireworksai** (dieses) | `:8000` | Fireworks Key Pool + Proxy |
| **SINator-heypiggy** | `:8002` | HeyPiggy Account Generator |
| **SINator-dashboard** | `:3000` | Tauri App, Provider-Switcher |

Start: `cd ~/dev/SINator-dashboard && ./start.sh` → :8000 + :8002 + :3000 + Tauri App
Build: `cd ~/dev/SINator-dashboard && ./build.sh` → /Applications/SINator.app

⚠️ Tauri Release App ist **statisch** — jedes Code-Update erfordert `./build.sh`.

---

*Last Updated: 2026-05-30 (V15.2 — Session Expiry Auto-Recovery + Dashboard Terminal Launch)*
*All learnings propagated to AGENTS.md, knowledge-base.md, and banned.md.*

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **SIN-Hermes-Provider-Bundle** (3253 symbols, 5007 relationships, 133 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/SIN-Hermes-Provider-Bundle/context` | Codebase overview, check index freshness |
| `gitnexus://repo/SIN-Hermes-Provider-Bundle/clusters` | All functional areas |
| `gitnexus://repo/SIN-Hermes-Provider-Bundle/processes` | All execution flows |
| `gitnexus://repo/SIN-Hermes-Provider-Bundle/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

---

## 🧠 Simone MCP — Code Intelligence & Automation

Simone MCP bietet zusätzliche Code-Analyse-Tools via MCP:

**Verfügbare Tools:**
- `sin_simone_mcp_symbol_search` — Symbol-Suche im gesamten Workspace
- `sin_simone_mcp_find_references` — Alle Referenzen zu einem Symbol finden
- `sin_simone_mcp_project_overview` — Workspace-Footprint + Dateitypen
- `sin_simone_mcp_structural_edit` — Strukturelle Code-Edits (LSP-grade)
- `sin_simone_mcp_memory_query` — Cloud Semantic Memory (Kontext + Analysen)
- `sin_simone_mcp_health` — Server-Status und Capabilities

**IMMER verwenden für:**
- `sin_simone_mcp_symbol_search` statt grep für Symbol-Suche
- `sin_simone_mcp_find_references` vor Refactoring
- `sin_simone_mcp_project_overview` für schnellen Codebase-Überblick
- `sin_simone_mcp_structural_edit` für sichere, strukturierte Edits

---

## 🔧 AKTUELLE FIXES (2026-05-30) — OTP/GMX Inbox Read ✅

### read_otp FUNKTIONIERT (6.45s, verified 2026-05-30)
```
OTP result: {"status": "success", "otp_url": "https://app.fireworks.ai/signup/confirm?...", "execution_time": "6.45s"}
```

### Alle Fixes im Überblick
1. **`return {{ → return {`** — Python interpretiert `{{...}}` als Set mit Dict darin → `TypeError: cannot use 'dict' as a set element`. Betroffen waren 2 return-Anweisungen in `read_otp()`. Fix: Einfache `{}` statt `{{}}`.
2. **`_pw_connect()` — Inbox-Priorität** — Neue Priority-Stufe: `navigator.gmx.net/mail?sid=` vor allen anderen GMX-Pages. Findet jetzt sofort den Inbox-Page statt `www.gmx.net/mail/#...`.
3. **`findHost()` Shadow Boundary** — Alte Walk-Funktion nutzte `parentElement` (bricht an Shadow-Boundary). Fix: `el.getRootNode().host` traversiert über Shadow-Grenzen hinweg zum `list-mail-item`.
4. **`_cdp_extract_url_from_email_body()` — OOPIF Type** — GMX Email Body lädt in `iframe`-type Target `gmxnet.mailbody-ui.de`, nicht `page`. Fix: `attach_to_iframe()` wiederhergestellt + Suche über `page` + `iframe` types.
5. **`ensure_gmx_inbox()` — Inbox-first** — Wenn Page bereits auf `bap.navigator.gmx.net/mail?sid=` (Inbox), wird direkt True returned ohne `page.goto()`.

### GMX Email Opener Skill + Tool (2026-05-30)
- Neue Funktion `GmxService.open_gmx_email()` in `gmx_service.py:945`
- CLI Tool: `tools/open_gmx_email.py`
- Skill: `~/.config/opencode/skills/gmx-email-open/SKILL.md`

### GMX Inbox = Cross-Origin Iframe (webmailer.gmx.net)
- Die Mail-Liste lädt NICHT im Hauptdokument, sondern in same-process iframe `webmailer.gmx.net`
- Playwright `frame.evaluate()` funktioniert (same-origin innerhalb des Portals)
- Email-Body lädt in **OOPIF** `gmxnet.mailbody-ui.de` — erreichbar via CDP `attach_to_iframe()`

### read_otp FUNKTIONIERT (6.45s, verified 2026-05-30)
```
OTP result: {"status": "success", "otp_url": "https://app.fireworks.ai/signup/confirm?...", "execution_time": "6.45s"}
```

### Alle Fixes im Überblick
1. **`return {{ → return {`** — Python interpretiert `{{...}}` als Set mit Dict darin → `TypeError: cannot use 'dict' as a set element`. Betroffen waren 2 return-Anweisungen in `read_otp()`. Fix: Einfache `{}` statt `{{}}`.
2. **`_pw_connect()` — Inbox-Priorität** — Neue Priority-Stufe: `navigator.gmx.net/mail?sid=` vor allen anderen GMX-Pages. Findet jetzt sofort den Inbox-Page statt `www.gmx.net/mail/#...`.
3. **`findHost()` Shadow Boundary** — Alte Walk-Funktion nutzte `parentElement` (bricht an Shadow-Boundary). Fix: `el.getRootNode().host` traversiert über Shadow-Grenzen hinweg zum `list-mail-item`.
4. **`_cdp_extract_url_from_email_body()` — OOPIF Type** — GMX Email Body lädt in `iframe`-type Target `gmxnet.mailbody-ui.de`, nicht `page`. Fix: `attach_to_iframe()` wiederhergestellt + Suche über `page` + `iframe` types.

### GMX Email Opener Skill + Tool (2026-05-30)
- Neue Funktion `GmxService.open_gmx_email()` in `gmx_service.py:945`
- CLI Tool: `tools/open_gmx_email.py`
- Skill: `~/.config/opencode/skills/gmx-email-open/SKILL.md`

### GMX Inbox = Cross-Origin Iframe (webmailer.gmx.net)
- Die Mail-Liste lädt NICHT im Hauptdokument, sondern in same-process iframe `webmailer.gmx.net`
- Playwright `frame.evaluate()` funktioniert (same-origin innerhalb des Portals)
- Email-Body lädt in **OOPIF** `gmxnet.mailbody-ui.de` — erreichbar via CDP `attach_to_iframe()`

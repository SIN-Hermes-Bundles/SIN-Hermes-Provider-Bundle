# SINator Knowledge Database — Lessons Learned

> "Once Verified = Read-Only. New code = New file. Learnings → Here."
> Last verified: 2026-05-30 — V15.1 COMPLETE: 223 Keys (95 available, 10 used, 118 suspended), ~140s avg

## 🟢 WHAT WORKS (V15.1 Playwright-native + Session Reuse)

### GMX Alias Rotation (~37s, Playwright-native)
- **Nav**: Playwright `ACCOUNT-AVATAR-NAVIGATOR` JS click → `dispatchEvent(mouseenter)` → Shadow DOM traversal "E-Mail Einstellungen" → Settings iframe "E-Mail-Adressen" → `3c.gmx.net` top-frame
- **Delete**: Playwright iframe `locator(f'text={alias}').hover()` → `locator('[title*="löschen"]').click(force=True)` → verify deletion
- **Create**: Playwright iframe `input[type="text"].fill()` → `button:has-text("Hinzufügen")`.click(force=True)` → verify `input_value() == ''`
- **Chrome Tab Cleanup**: Nach jeder Rotation ALLE non-essential Tabs schließen (nur Dashboard + 1 GMX-Inbox bleiben)

> **⚠️ WICHTIG:** CUA `find_cua_window` funktioniert NICHT für Navigation — Chrome-Tab-Titel ist leer bei programmatischen Tabs. Reiner Playwright-Ansatz für Navigation.

### Fireworks Signup (Playwright)
- **Email**: `input[name="email"].fill()` → `button:has-text("Next")`.click()`
- **Password**: 2x `input[type="password"].fill()` → `button:has-text("Create Account")`.click()`
- **OTP Poll**: 25 attempts × 8s = 200s max. `read_otp(sender_filter="fireworks")` via CDP OOPIF
- **Verify**: `verify_account(url)` → opens URL in new tab via Playwright
- **Fallback**: If OTP not found → `partial` status (account unverified but often loginable)

### Fireworks Login + Onboarding (Playwright + CUA)
- **Login**: `/login` → `input[name="email"]` + `input[name="password"]` → `button:has-text("Next")`
- **Names**: CUA `type_text` → search "First" + "Last" (NOT "Name" — matches "Company Name"!) OR Playwright `type()` as fallback
- **Terms checkbox**: `<button role="checkbox">` + native `el.click()` (NOT `check()` — Radix UI ignoriert JS click). Chrome Password Save Dialog vorher dismissen.
- **Continue/Next**: 3 Strategien: 1) `button:has-text("Continue")` + `is_visible() + not is_disabled()`, 2) `button[type="submit"]`, 3) Case-insensitive scan aller Buttons. 2s wait nach Terms-Checkbox für React re-render.
- **Use-Cases**: `label:has-text("{use_case}")` als primäre Strategie (Click auf Label triggert echten Input). Fallback: `input[type="checkbox"]` mit `aria-label`. Mindestens 1 pro Gruppe.
- **Submit/Get $5**: `button:has-text("Submit")` / `has-text("Get $5")` + Fallback case-insensitive scan
- **CUA Fallback**: If CUA Submit fails → Playwright fills form + Submit
- **Session Reuse**: `login_fireworks()` gibt `page`, `playwright`, `browser` zurück → `create_api_key()` wiederverwendet diese

### Fireworks API Key (Playwright + Session Reuse)
- **Session Reuse**: `create_api_key(key_name, page=login_result['page'], playwright=login_result['playwright'], browser=login_result['browser'])` — Verhindert Login-Redirect auf API Key Seite
- **URL**: `/settings/users/api-keys` (NOT `/settings/workspace/api-keys`!)
- **Create button**: `button:has-text("Create API Key")`.click(force=True)` → `[role="menuitem"]:has-text("API Key")`.click()`
- **Name**: `input[name="name"].fill()` → Wait 1s (React re-render) → disabled→enabled polling
- **Generate**: 15×1s poll until `button:has-text("Generate")` not disabled → click(force=True)
- **Extract**: `re.findall(r'fw_[a-zA-Z0-9]{20,}', page.evaluate("document.body.innerText"))` with 10s DOM-polling
- **Error Handling**: "Missing API Key Name!" Modal → Close → retry fill + Generate

### Session Management
- **GMX Login**: Playwright form fill (not CDP!)
- **Fireworks Logout before Signup**: `page.context.clear_cookies()` for fireworks domain + `localStorage.clear()` + force navigate `/logout` URLs
- **Tab cleanup**: After each rotation, close all non-essential tabs
- **Session Reuse**: `login_fireworks()` Session an `create_api_key()` übergeben — keine neue Page erstellen!

### Config Manager (V12)
- **Singleton** `get_config()` reads `data/config.json`
- **Fields**: `gmx_email`, `gmx_password`, `fireworks_password`
- **API**: `GET/POST /api/v1/config` (public, no Auth-Token)
- **Rotation**: Reads Config → passes `--gmx-email`, `--gmx-password`, `--password` to rotate.py

### Pool-Proxy /v1/models (V13)
- **Handler**: `_handle_v1_models()` reads `~/.hermes/models_dev_cache.json`
- **Routes**: `/v1/models` + `/inference/v1/models` (before Catch-All)
- **PUBLIC_PROXY_PATHS**: includes `/v1/models`
- **Hermes**: `custom:fireworks` provider probes `/v1/models` live → Model-Picker shows 12 FW models

### Chat-Assistant (V12)
- **Rust Command** `chat_send` — bypasses Tauri WebView Fetch block
- **Model**: `accounts/fireworks/models/gpt-oss-120b` ($0.15/M, cheapest Serverless)
- **System-Prompt**: `chat-system-prompt.txt` (include_str! in Rust)
- **Live-Stats**: Rust fetches Pool-Stats (:8000) + Backend-Health → injects into System-Prompt
- **Fallback**: `content` + `reasoning_content` (Reasoning models)
- **No Streaming** — simple invoke Return

## 🔴 KNOWN ISSUES (2026-05-30)

### Account Suspension (Spending Limit)
Fireworks suspends accounts when $5 Credits are exhausted:
```
Account golden-cobra-560-66c is suspended, possibly due to reaching the monthly
spending limit or failure to pay past invoices.
```
- **Workaround**: `POST /pool/report` marks Key as suspended → Backend atomically leases replacement
- **No Recovery** — Account is dead, new account needed

### OTP Delay (Up to 200s)
Fireworks verify email can take up to 180s to arrive.
- **Fix**: 25 × 8s = 200s polling in `signup_fireworks()`
- **Fallback**: `partial` status — account is unverified but often loginable

### Unverified Account = API Key Blocked
Account created but unverified → API Key page redirects to `/login`
- **Fix**: Verify URL must be opened (or account is already verified)
- **Workaround**: After `partial` signup → `login_fireworks()` tries anyway
- **Session Reuse**: Neue Page ohne Cookies = Login-Redirect. Use Session Reuse zwischen Login und API Key!

### Chrome Tab Overload (FIXED V12)
After 4h batch rotation → 37+ tabs → Chrome overloaded → Playwright connect timeout.
- **Fix**: `rotate.py` cleans up ALL non-essential tabs after each rotation.

### Tauri WebView Fetch Blocked
`fetch("http://localhost:8888/...")` from Tauri WebView → `TypeError: Load failed`
- **Workaround**: Rust Command `chat_send` makes the HTTP call
- **Also banned**: `listen()` (ACL denied), Next.js API Routes (not in Static Export)

## 🔴 BANNED / BROKEN

### Playwright Anti-Patterns (V15.1)
| ❌ Banned | Reason |
|-----------|--------|
| `check()` on React-Checkbox | Radix UI `<button role="checkbox">` ignoriert JS click. Use native `el.click()` |
| `input[type="checkbox"]` with `aria-label` for Use-Cases | Fireworks: aria-label Matching does NOT work. Use `label:has-text("{use_case}")` |
| `label:has-text("Terms")` for Terms-Checkbox | Matches "Terms of Service" Link, not checkbox. Use `button[role="checkbox"]` |
| Simple button scan for Continue/Submit | React re-renders → hits wrong button. Use 3-stage strategy |
| `create_api_key()` without Session Reuse | New page = no cookies → API Key page redirects to `/login`. Use `login_fireworks()` session |
| `return {{...}}` instead of `return {...}` | Python: `{{...}}` = Set with Dict → `TypeError` |
| `parentElement` for Shadow DOM | Breaks at shadow boundary. Use `el.getRootNode().host` |
| `fill()` on React inputs without `click()` first | React state not updated |
| `input[type="email"]` on Fireworks | Input has NO type attribute |
| `text=CREATE` as button selector | Matches Cookie-Banner |
| `browser.new_page()` for every step | Tab explosion → Chrome overload |
| `page.goto()` on 3c.gmx.net directly | Triggers IAC Anti-Automation |

### CUA Anti-Patterns
| ❌ Banned | Reason |
|-----------|--------|
| Hardcoded element_index | React re-renders → indices change |
| `type_text` on React Email inputs | React ignores CUA keyboard events |
| `find_cua_window(title_keywords=["FreeMail"])` | Chrome tab title is EMPTY |
| CUA for Navigation | Tab title empty → find fails |
| CUA for Web-Content (Checkboxes/Buttons) | `get_window_state()` shows Chrome AX-Tree (Tabs, Bookmarks), NOT Web-Content |

### Tauri v2 Banned Patterns
| ❌ Banned | Reason |
|-----------|--------|
| `__TAURI_INTERNALS__` Check | Empty in Production Build |
| Next.js API Routes | Not in Static Export |
| `listen()` for Streaming | ACL denied |
| `fetch()` to localhost:8888 | WebView blocked |
| `kimi-k2p5` as Chat model | `reasoning_content` instead of `content` |
| Frontend-Fetch without Auth-Token | 401 |

## 📊 TOOL COMPARISON (V15.1)

| Tool | Nav | Input Fill | Button Click | React-CB (Radix) | Use-Cases | Verify |
|------|:---:|:----------:|:------------:|:----------------:|:---------:|:------:|
| Playwright | ✅ | ✅ | ✅ | ✅ (native el.click) | ✅ (label:has-text) | ✅ |
| CUA | ⚠️ | ✅ (type_text) | ✅ (dialogs) | ❌ (kein Web-Content) | ❌ | ❌ |
| CDP | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (OOPIF) |
| JS evaluate | ❌ | ✅ (nativeSetter) | ⚠️ | ❌ | ❌ | ✅ |
| Rust Command | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Best Hybrid (V15.1): Playwright nav + Playwright form + Playwright for Radix UI (native el.click) + Playwright for Use-Cases (label:has-text) + CDP for OTP/OOPIF + Session Reuse
### Chat: Rust Command (not Frontend Fetch!)

### Performance: V9 → V15.1
| Metric | V9 | V11 | V12 | V14 | V15.1 |
|--------|:--:|:---:|:---:|:---:|:-----:|
| Pool Size | 45 | 112 | 146 | 218 | 223 |
| Cycle Time | ~173s | ~210s | ~180s | ~130s | ~140s |
| GMX Rotation | CDP | Playwright | Playwright | Playwright-native | Playwright-native |
| Fireworks | CDP | Playwright+CUA | Playwright+CUA | Playwright+CUA | Playwright+CUA |
| Credentials | Hardcoded | Config Manager | Config Manager | Config Manager | Config Manager |
| Chat | N/A | Rust Command | Rust Command | Rust Command | Rust Command |
| Proxies | 1× :8888 | 1× :8888 | 3× :8888-:8890 | 10× :8888-:8897 | 10× :8888-:8897 |
| Swap Atomicity | report+lease separate | report+lease separate | Atomic | Atomic | Atomic |
| Pool-Router | N/A | N/A | Single endpoint | Single endpoint | Single endpoint |
| Session Reuse | N/A | N/A | N/A | ❌ | ✅ |

## 🔧 VERIFIED WORKING COMMITS

| Commit | Date | Status |
|--------|------|--------|
| `HEAD` | May 30 | ✅ **LATEST**: V15.1 — Session Reuse + Use-Cases Fix, 223 Keys, ~140s |
| V14 | May 29 | ✅ V14: Playwright-native, 10 Proxies, 218 Keys, ~130s |
| V12 | May 26 | ✅ V12: Shadow DOM Nav, Atomic Swap, 146 Keys, Config Manager |
| V11 | May 25 | ✅ V11: Config Manager, Chat, Keychain, 112 Keys |
| V10 | May 24 | ✅ V10: CUA PID Targeting, ~204s E2E |
| V9 | May 23 | ✅ V9: Sleep-Reduction + Bugfixes, 45 Keys |

## 🚀 QUICK REFERENCE

```bash
# Start Chrome (Profile 901, Port 9222)
nohup "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir="/Users/jeremy/Library/Application Support/Google Chrome" \
  --profile-directory="Profile 901" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  > /tmp/chrome_sinator.log 2>&1 &

# Full E2E (reads Config from data/config.json)
python tools/rotate.py

# API Key URL
https://app.fireworks.ai/settings/users/api-keys

# Pool Stats
curl -s http://localhost:8000/pool/stats | python3 -m json.tool

# Config
curl -s http://localhost:8000/api/v1/config | python3 -m json.tool

# Pool-Proxies (10 instances)
Lokal: http://localhost:9998/inference/v1    → https://sinatorpool-router.delqhi.com/inference/v1
# apiKey (alle Macs): <DEIN_API_KEY>

# List models (via Pool-Proxy)
curl http://localhost:9998/inference/v1/models \
  -H "Authorization: Bearer <DEIN_API_KEY>"
```

## 🔧 ARCHITECTURE (V15.1)

```
SINator-fireworksai/        ← Backend (:8000) + 10× Proxy (:8888-:8897) + Rotation
SINator-dashboard/          ← Next.js + Tauri v2 App (Dashboard + Chat)
sinator-pages/              ← Landing Page (:8040)

Services (LaunchAgents):
  com.sinator.backend      :8000   FastAPI
  com.sinator.pool-router  :9998   Pool-Router (ThreadingMixIn + Failover)
  com.sinator.pool-proxy-{8888..8897} :8888-:8897  10× aiohttp SSE + silent swap
  com.sinator.pages        :8040   Landing Page
  com.sinator.chrome       :9222   Chrome Profile 901

Tunnel Subdomains:
  sinatorpool-router.delqhi.com  → :9998 (Pool-Router) → 10× Proxys :8888-:8897
  sinator.delqhi.com       → :8000 + :8040
```

---

*Last Updated: 2026-05-30 (V15.1 — Session Reuse + Use-Cases Fix)*

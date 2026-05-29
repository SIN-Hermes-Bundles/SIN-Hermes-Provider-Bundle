# 🚫 BANNED — Verbotene Methoden & Patterns

> **NIEMALS** diese Methoden verwenden. Sie wurden ALLE getestet und sind fehlgeschlagen.

---

## 🚫 BANNED: Playwright-native Anti-Patterns (2026-05-29)

| ❌ Verboten | Grund |
|------------|-------|
| Playwright `check()` auf React-Checkbox | "Clicking did not change state" — React-CB ignoriert JS-Click. Use CUA `AXPress` oder Playwright `click(force=True)` |
| Playwright `fill()` auf React-Inputs ohne `click()` vorher | React-State nicht aktualisiert. Use `click()` + `fill()` oder `type(delay=50)` |
| `page.locator('input[type="email"]')` auf Fireworks | Input hat KEIN type-Attribut. Use `input[name="email"]` |
| `page.locator('input[type="password"]')` als einziger Selector | Es gibt 2 Password-Inputs (Password + Confirm). Use `input[name="password"]` |
| `text=CREATE` als Button-Selector | Matcht Cookie-Banner "Create profiles for personalised advertising" |
| `text=E-Mail` als Page-Link | Matcht News-Artikel (Text im Content, nicht Nav-Link) |
| `text=Next` als Submit-Button | Matcht Cookie-Banner "Next" — use `button[type="submit"]` + text-check |
| `page.goto()` auf 3c.gmx.net direkt | Triggert IAC Anti-Automation. Use shadow DOM navigation via Playwright |
| `browser.new_page()` für jeden Schritt | Tab-Explosion → Chrome überlastet. Reuse pages, close non-essential tabs |
| `_click_text()` Helper aus V5/V7 | Unreliable text-matching. Use Playwright-native locators |
| `cua-driver` für Navigation | Tab-Titel ist leer bei programmatischen Tabs. Use Playwright für Navigation |
| `find_cua_window(title_keywords=["FreeMail"])` | Chrome-Titel ist LEER für neue Tabs. Use `get_page_target()` mit URL-Matching |

---

## 🚫 BANNED: Tauri v2 Patterns (2026-05-25)

| ❌ Verboten | Grund |
|------------|-------|
| `__TAURI_INTERNALS__` in `BACKEND_URL` Check | Existiert im Production Build nicht → `BACKEND_URL` wird leer → alle Fetches failen |
| Next.js API Routes im Tauri Static Export | `frontendDist: "../out"` = statischer Export, `/api/*` Routen existieren nicht |
| Tauri Event `listen()` für Chat-Streaming | ACL `plugin:event|listen not allowed` — Permission existiert aber JS API braucht anderen Scope |
| `fetch()` von Tauri WebView zu `localhost:8888` | Tauri v2 blockiert externe Fetches per Default — braucht Rust Command statt Frontend-Fetch |
| `kimi-k2p5` als Chat-Modell | Reasoning-Modell — denkt 20-30s, Antwort kommt in `reasoning_content` statt `content` |
| `gpt-oss-120b` mit `max_tokens=50` | Zu kurz — Reasoning wird abgeschnitten bevor die Antwort kommt |
| Frontend `fetch` zu `localhost:8000` ohne Auth | `/api/v1/config` war nicht in `public_prefixes` → 401 → GMX Passwort wurde nicht geladen |

**✅ Korrektur:** Rust `chat_send` Command (kein Event nötig), `BACKEND_URL` immer `"http://localhost:8000"`, `/api/v1/config` in `public_prefixes`, `gpt-oss-120b` mit `max_tokens=2048`

---

## 🚫 BANNED: Health Check Side-Effects (2026-05-23)

| ❌ Verboten | Grund |
|------------|-------|
| `GET /pool/health` ruft `mark_used()` auf | Destruktiver Side-Effect! 7 Keys zerstört am 2026-05-23 |
| Dashboard `loadDashboard()` ruft `/pool/health` | Überschreibt stats-Anzeige mit health-Daten |
| `PoolManager` ohne `reload()` | Singleton hat stale State, sieht keine externen Änderungen |
| `_purge_gmx_cookies()` löscht Master-Backup | Überschreibt `backup/session/gmx-cookies-master.json` |
| `update_credits()` hat NULL Callers | Credits werden nie gezogen — alle Keys zeigen `credits_remaining=6.0` |

**✅ Korrektur:** Health-Endpoint ist read-only. PoolManager ruft `reload()` vor jeder public Methode.

---

## 🚫 BANNED: E2E Flow Patterns (2026-05-22)

| ❌ Verboten | Grund |
|------------|-------|
| GMX Rotation OHNE vorherigen Logout-Check | Redirect zu Account-Home statt Signup-Form |
| CUA `"Name"` statt `"First"` + `"Last"` | Matcht "Company Name" zuerst → falsches Feld |
| Hardcodierte CUA-Indizes (129, 137, etc.) | React re-rendered → Indizes ändern sich |
| `_re` Import NUR global | Wird in inner function scope nicht gefunden |
| `input[type="email"]` auf Fireworks | Input hat KEIN type-Attribut → `input[name="email"]` |
| `/settings/workspace/api-keys` | 404 → `/settings/users/api-keys` |
| `text=CREATE` als Button-Selector | Matcht Cookie-Banner |
| `pkill -9 -f "Google Chrome"` | Killt User-Chrome → Profil-Lock → Session tot |
| 37 Tabs offen lassen | Chrome überlastet → Playwright connect timeout |
| CDP `Network.deleteCookies` auf ALLE Domains | Löscht GMX-Session! Nur Fireworks-Domain löschen |

---

## 🚫 BANNED: OTP/Email-Lesung (2026-05-12)

**GMX MailCheck Extension + CDP OOPIF ist DER EINZIG ZULÄSSIGE WEG für OTP.**

| ❌ Verboten | Grund |
|------------|-------|
| HTTP `mailbody/tmai{id}/true;jsessionid=...` | GMX REST API gibt 403 |
| CDP `DOM.performSearch` + `describeNode` auf Webmailer | Hängt auf 3c.gmx.net |
| Shadow DOM Traversal für Email-Zugriff | Wicket blockiert alle JS-Events |
| `read_otp()` OHNE Extension-Methode | HTTP-API ist tot |
| `lightmailer-bs.gmx.net` URLs | HTTP 500 errors |

**✅ Erlaubt:** Extension-Popup öffnen → Email per JS klicken → `mailbody-ui.de` OOPIF → Verify-URL extrahieren

---

## 🚫 BANNED: Chrome Session Management (2026-05-11)

| ❌ Verboten | Grund |
|------------|-------|
| Chrome mit Default user-data-dir starten | `DevTools remote debugging requires a non-default data directory` |
| Nur Profil-Subfolder kopieren (ohne Local State) | Chrome erstellt NEUES Profil statt Profile 901 zu verwenden |
| Cookie-Injection in fremdes Profil | Cookies sind profilgebunden verschlüsselt (macOS Keychain) |
| Symlink für user-data-dir | Symlink bricht Cookie-Entschlüsselung |
| `puppeteer.launch()` statt `spawn()` | Setzt `--enable-automation` → GMX Bot-Detection |
| `waitForNavigation()` bei auth.gmx.net | GMX auth ist SPA — keine Page-Navigation |
| `pkill -9 -f "Google Chrome"` | Killt User-Chrome → Profil-Lock |

---

## 🚫 BANNED: CDP-Only Anti-Patterns (HISTORISCH — 2026-05-21)

> **Diese Bans sind aus V5/V7. Aktueller Code (V14) nutzt Playwright-native — CDP wird nur noch für OTP-Extension und Cookie-Management verwendet.**

| ❌ Verboten (historisch) | Grund |
|--------------------------|-------|
| CDP `Runtime.evaluate` auf GMX accessible pages | Gibt `{}` zurück wenn Accessibility-Mode aktiv |
| CDP `Page.navigate` zu GMX URLs | Triggert Bot-Detection (Akamai/DataDome) |
| CDP `Input.dispatchKeyEvent` | GMX React-Inputs ignorieren |
| CDP `DOM.performSearch` auf 3c.gmx.net | Hängt (kein CDP Response) |
| CDP `Input.dispatchMouseEvent` für Navigation | GMX ignoriert CDP für Nav |
| JS `nativeSetter` ohne `dispatchEvent('input')` | React-State nicht aktualisiert |
| Hartcodierte Koordinaten `(350,340)` | Klickt ins Leere |
| AX tree_line als element_index | Regex `\[(\d+)\]` extrahiert tree_line statt element_index |

---

## 🚫 BANNED: READ-ONLY Code ändern

```
# Flow #1 (gmx_service.py), Flow #2 (fireworks_service.py), Flow #3 (OTP extraction)
# sind VERIFIED und funktionieren. NIE ändern außer es gibt einen konkreten Bug-Report.

# Breaked am 2026-05-10: Agent versuchte "DOM exploration" für Shadow-DOM input
# → rewrite _navigate_to_all_email_addresses mit 75-line PFAD-Navigation
# → Flow #1 komplett gebrochen
# → 11 files reverted auf commit cf146a6 (alles verloren!)
```

**Regel:** ONCE VERIFIED = READ-ONLY. Nur ändern wenn: (a) konkreter Bug-Report, (b) GMX die UI ändert, (c) neue Use-Case erfordert es.

---

## 🚫 BANNED: macos-use Agent (2026-05-21)

| ❌ Verboten | Grund |
|------------|-------|
| `agent.invoke()` mit LLM | Tool-Validierung broken (loc:Input should be a valid list) |
| Agent Tool calls | Pydantic `list[int]` validation fails on LLM JSON output |
| Chromium launch via Agent | Chrome bereits offen; App-Tool crashed |

**✅ Erlaubt:** CUA direkt für OS-Level-Klicks (kein LLM-Agent nötig)

---

## ✅ KORREKTE METHODE (siehe AGENTS.md für Details)

**⚠️ WICHTIG: Chrome NIEMALS killen! pkill -9, SIGKILL, `kill` = ABSOLUT BANNED!**
Session persists across Chrome restarts via Profile 901 cookies.

```bash
# Chrome STARTEN mit ORIGINAL Profil 901 (KEINE Kopie!)
nohup "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir="/Users/jeremy/Library/Application Support/Google Chrome" \
  --profile-directory="Profile 901" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  > /tmp/chrome_sinator.log 2>&1 &

sleep 6 && curl -s http://127.0.0.1:9222/json/version
```

**⚠️ WICHTIG:** NIEMALS Profile kopieren oder nach /tmp verschieben!
Original-Profil 901 nutzen — Cookies sind an Original-Pfad gebunden (macOS Keychain).

---

*Last Updated: 2026-05-29 (V14 — Playwright-native)*

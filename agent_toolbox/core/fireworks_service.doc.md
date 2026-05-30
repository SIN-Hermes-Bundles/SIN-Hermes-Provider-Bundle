# fireworks_service.py

Fireworks AI Account-Management: Signup, Login, Onboarding, API Key Erstellung. Hybrid aus Playwright (Form-Interaktion) und CUA (nur für AXTextField).

## Berührt

- `gmx_service.py` — Holt Alias + OTP für Signup
- `pool_manager.py` — Speichert neuen API-Key im Pool
- `cua_helper.py` — CUA Window Detection für Onboarding
- `tools/rotate.py` — Ruft signup → login → create_api_key

## Config / Limits

- `OTP_POLL_ATTEMPTS: 25` × 8s = 200s max
- Account Status: `partial` (unverified), `active`, `suspended`
- Suspended wenn $5 Credits aufgebraucht — Key dann `used` markieren

## Wichtige Entscheidungen

- **CUA NUR für Names (AXTextField):** `get_window_state` zeigt Chrome UI (Tabs, Bookmarks), NICHT Web-Content. Nur AXTextField-Elemente sind im Chrome-AX-Tree sichtbar. Checkbox/Button existieren dort nicht → müssen via Playwright geklickt werden.
- **Checkbox-Strategie (Radix UI):** Terms-Checkbox ist ein `<button role="checkbox">`, NICHT `<input type="checkbox">`. Nur native `el.click()` auf dem Button triggert den React/Radix State-Change und rendert das SVG-Icon. Playwright `btn.click()`, `btn.click(force=True)`, und `dispatchEvent` toggeln den State entweder gar nicht oder sofort zurück. Use-Cases-Checkboxes (Step 2) sind echte `<input type="checkbox">` — dort funktioniert `el.click()` nativ.
- **Fireworks Session vor Signup löschen (CDP-Level):** `ctx.clear_cookies()` + `ctx.add_cookies(non_fw_cookies)` + `localStorage.clear()` vor `/signup` goto. Löscht auch `httpOnly`/`Secure` Cookies. Fallback: force navigate `/logout` URLs.
- **Onboarding komplett via Playwright** (CUA kann nur AXTextField — Chrome UI, nicht Web-Content)
- **Chrome Password Save Dialog:** Vor Onboarding dismissen ("Nie"/"Never" Button finden und klicken)

## Onboarding Flow

1. **Name-Felder** (firstName/lastName) — Playwright `type()` mit delay
2. **Terms-Checkbox** — `button[role="checkbox"]` + native `el.click()` (Radix UI)
3. **Continue/Next** — 3 Strategien: 1) `button:has-text("Continue")` + `is_visible() + not is_disabled()`, 2) `button[type="submit"]`, 3) Case-insensitive Scan aller Buttons. 2s wait nach Terms-Checkbox für React re-render.
4. **Use-Cases** — `label:has-text("{use_case}")` als primäre Strategie (Click auf Label triggert echten Input). Fallback: `input[type="checkbox"]` mit `aria-label`. (Prototype, Flexible capacity, Conversational, Search)
5. **Submit/Get $5** — 2 Strategien: `button:has-text("Submit")` / `has-text("Get $5")` + Fallback case-insensitive Scan aller Buttons
6. **Redirect-Check** — 10×2s Poll auf `home`/`account`/`settings` in URL
7. **Force-Navigate** — Falls kein Redirect: direkt zu API-Keys Seite

## API Key Erstellung

- **Session Reuse:** `create_api_key(key_name, page=None, playwright=None, browser=None)` akzeptiert optional `page`/`playwright`/`browser` von `login_fireworks()`. Wiederverwendet die Session statt neue Page zu erstellen. Verhindert Login-Redirect auf API Key Seite.
- `_generate_and_poll_key()` — Generate-Button klicken, 15 Retries mit 1s wait
- Polling auf Key-Textarea oder Input-Feld via `fw_...` regex
- Missing-Name Modal: Name eintragen + Retry
- Ergebnis: `{api_key: "fw_...", name: "..."}`

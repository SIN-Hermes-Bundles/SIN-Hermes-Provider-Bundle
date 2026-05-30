# SINator Fireworks AI Rotator — Status Report (2026-05-30)

## 1. Pool State

| Metrik | Wert |
|--------|------|
| Total Keys | 225 |
| Available | 20 |
| Used | 11 |
| Suspended | 194 |
| Latest | `2026-05-30T06:55:00Z` (manual-key-2026-05-30) |

### Problem: 87% Suspended Rate
- Fast alle Keys sind **suspended** (Spending Limit erreicht — $5 Credits aufgebraucht)
- Suspended-Reason: `spending_limit` oder `unknown`
- **Available-Pool ist quasi leer** — 18 Keys übrig, aber die werden schnell aufgebraucht sein
- Kein Mechanismus für Auto-Key-Recovery nach Suspension

### Problem: Leased-Fields tot
- Pool hat `lease_id`, `leased_at`, `leased_to`, `leased_until` — alle = 0 belegt
- Legacy aus alter `leased`-Architektur, nie entfernt
- Füllt nur JSON auf

---

## 2. Architecture (V15.1)

```
tools/rotate.py
  → GmxService.login()           Playwright GMX Login
  → GmxService.rotate_alias()    Playwright alias CRUD (iframe)
  → signup_fireworks()           Playwright + CUA
  → login_fireworks()            Playwright + CUA (Onboarding)
  → create_api_key()             Playwright API Key page → polling
  → PoolManager.add_key()        JSON speichern

proxy/server.py
  → Docker-artige Key-Lease aus Pool
  → SSE Streaming für chat/completions
  → /v1/models Handler (Hermes Integration)
```

### Key Files

| Datei | Zeilen | Rolle |
|-------|--------|-------|
| `gmx_service.py` | 959 | GMX Login, Alias CRUD, OTP Read |
| `fireworks_service.py` | 634 | FW Signup, Login, Onboarding, API Key |
| `cdp_client.py` | 335 | Raw CDP WebSocket (cross-origin iframes) |
| `pool_manager.py` | 519 | Pool-Management, Lease/Report |
| `proxy/server.py` | 597 | aiohttp Proxy mit SSE |
| `tools/rotate.py` | 109 | Rotation Orchestrator |

---

## 3. Critical Problem: OTP-Read (GMX Inbox)

### Der Kern des Problems
GMX lädt die Mail-Liste **nicht im Hauptdokument**, sondern in einem **cross-origin iframe** (`webmailer.gmx.net`) mit **3 Ebenen Shadow DOM**:

```
navigator.gmx.net (Hauptseite)
  └── <iframe webmailer.gmx.net>  ← cross-origin!
        └── <list-mail-box> (Custom Element)
              └── #shadow-root (open)
                    └── <list-mail-item> (Custom Element)
                          └── #shadow-root (open)
                                └── ... Email Content ...
```

### Warum Playwright scheitert
| Methode | Problem |
|---------|---------|
| `page.locator('text=fireworks')` | Findet 0 Items (cross-origin iframe + Shadow DOM) |
| `frame.evaluate()` | CORS blockiert JS-Zugriff auf cross-origin webmailer iframe |
| JS `querySelectorAll` im page context | Sieht nur Hauptdokument, nicht iframe-Inhalt |

### CDP-Lösung (aktuell implementiert)
Der einzige Weg: **CDP `attach_to_iframe("webmailer.gmx.net")`** + `Runtime.evaluate` im iframe-Kontext.

```python
cdp = CDPClient(ws_url)
attached = await cdp.attach_to_iframe("webmailer.gmx.net")
if attached:
    wm_sid, wm_target = attached
    # JS im webmailer Kontext — Shadow DOM Walk + Click
    result = await cdp.evaluate(wm_sid, js_code)
```

### Status: 🔴 NICHT GETESTET
- Implementiert in `read_otp()` (Zeile 781-891)
- `_cdp_extract_url_from_email_body()` (Zeile 689-731) als Fallback
- **Nicht getestet** — der vorherige Testlauf scheiterte mit `page.reload()` (FIXED)
- Unklar ob die JS Shadow-DOM-Traversierung im webmailer iframe funktioniert

### Risiko: `page.goto()` killt Session
- `_ensure_gmx_inbox()` verwendet `page.goto("https://navigator.gmx.net/mail")` als Fallback
- `page.goto()` navigiert weg → Session-Cookie/Token verloren → GMX zeigt Login-Seite
- Das ist **das größte Risiko** im aktuellen Flow

---

## 4. Bekannte Probleme (nach Criticalität)

### 🔴 HIGH: Keine Available Keys mehr in Kürze
- 20 von 225 Keys bleiben
- Suspended-Keys werden nicht auto-erkannt/proaktiv aus Pool entfernt
- Rotation produziert Keys, die sofort suspended werden (FW erkennt Pattern?)

### 🔴 HIGH: GMX Login Session instabil
- GMX killt Session bei `page.goto()` / Navigation
- Recovery nur via Cookie-Backup (Master-Backup-Lösung)
- `check_session()` verwendet `page.goto("https://www.gmx.net/")` → killt auch Session

### 🟡 MEDIUM: `check_session()` zerstört Session
```python
async def check_session(self, cdp_port: int = 9222) -> Dict[str, Any]:
    page = await self._pw_connect(cdp_port)
    await page.goto("https://www.gmx.net/", ...)  # ← DAS killt die Session!
```
Fix: CDP `Runtime.evaluate` verwenden, nicht `page.goto()`

### 🟡 MEDIUM: Fireworks Onboarding instabil
- CUA findet Checkboxen nicht immer (React Custom Components ohne AX-IDs)
- Playwright-Fallback existiert, aber manchmal fehlerhaft
- Besonders betroffen: User-Cases + Research-Fragen im Onboarding

### 🟡 MEDIUM: Double-Key-Waste trotz Fix
- Atomic Report+Lease eingebaut, aber bei Timeout in `login_fireworks()` kann Key orphaned bleiben
- Proxy `_swap_key()` hat race condition bei gleichzeitigen Requests

### 🟢 LOW: Dead Code in Pool
- `lease_id`, `leased_at`, `leased_to`, `leased_until` — nie belegt
- Cookie-basierte Session-Management (`cookie_manager.py`, `_inject_cookies()`) — tot
- `COOKIE_FILE` Pfad-Konstanten — legacy

### 🟢 LOW: Test-Skripte in `debug/` und `tools/test_otp_mailcheck.py`
- Nicht ins Repo committed (`.gitignore` fehlte für `debug/`)
- `test_otp_mailcheck.py` nutzt MailCheck Extension (veraltet)

---

## 5. Co-Docs Status ✅

| Datei | Doc.md | Status |
|-------|--------|--------|
| `agent_toolbox/core/gmx_service.py` | `gmx_service.doc.md` | ✅ |
| `agent_toolbox/core/fireworks_service.py` | `fireworks_service.doc.md` | ✅ |
| `agent_toolbox/core/cdp_client.py` | `cdp_client.doc.md` | ✅ |
| `agent_toolbox/core/pool_manager.py` | `pool_manager.doc.md` | ✅ |
| `tools/rotate.py` | `rotate.doc.md` | ✅ |
| `proxy/server.py` | `server.doc.md` | ✅ |

---

## 6. Skill Status ✅

| Skill | Location | Status |
|-------|----------|--------|
| `sin-codocs` (OpenCode) | `~/.config/opencode/skills/sin-codocs/SKILL.md` | ✅ installiert |
| `sin-codocs` (Infra) | `Infra-SIN-OpenCode-Stack/skills/sin-codocs/SKILL.md` | ✅ gepusht |

---

## 7. Erledigte Fixes (2026-05-30)

| Fix | Status |
|-----|--------|
| `check_session()` — `page.goto` → CDP `Runtime.evaluate` | ✅ |
| `_ensure_gmx_inbox()` — `page.goto`-Fallbacks entfernt, CDP Target Discovery + SPA-Klicks | ✅ |
| `_inject_cookies()` — Dead Code entfernt | ✅ |
| `.gitignore` — debug, test_otp excluded | ✅ |
| Pool `lease_*` fields — aktiv genutzt (kein Dead Code) | ⏭️ behalten |
| OTP `read_otp()` — Playwright frame API für same-process webmailer iframe (statt CDP attach_to_iframe) | ✅ |
| `_pw_connect()` — bevorzugt logged-in GMX pages (DOM-Check auf "Sie sind eingeloggt") | ✅ |
| Consent-Management in `_ensure_gmx_inbox()` | ✅ |

## 8. Nächste Schritte

1. 🔴 **OTP mit realem Signup testen** — aktuell kein Fireworks OTP im Postfach
2. 🔴 **Full rotate.py testen** — E2E: Login → Alias → Signup → OTP → API Key
3. 🟡 **Suspended Key Removal** — Keys mit `suspended=true` automatisch aus Pool entfernen

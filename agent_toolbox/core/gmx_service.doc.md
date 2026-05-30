# gmx_service.py

GMX E-Mail Service für Alias-Rotation + OTP-Read (Playwright-native, V14 2026-05-30).

- **Alias-Rotation**: Playwright iframe-Interaktion via webmailer.settings frame
- **OTP/Verify-URL**: Playwright frame.evaluate() für webmailer (same-process iframe) + CDP OOPIF für mailbody-ui.de
- **Email-Öffnen**: `open_gmx_email()` — Shadow DOM Walk + findHost() für LIST-MAIL-ITEM

## Berührt

- `cdp_client.py` — CDP OOPIF attach für `gmxnet.mailbody-ui.de`
- `fireworks_service.py` — übergibt Alias für Signup
- `tools/rotate.py` — Orchestriert Alias-Erstellung + Signup
- `tools/open_gmx_email.py` — CLI Tool für Email-Öffnen

## Config / Limits

- `MAX_OTP_RETRIES: 25` — Polls alle 8s = 200s max (read_otp)
- `GMX_FREEMAIL_ALIAS_LIMIT: 1` — Nur ein Alias gleichzeitig
- OTP liest aus `webmailer.gmx.net` (same-process iframe → Playwright frame.evaluate) + `gmxnet.mailbody-ui.de` (OOPIF → CDP)

## Wichtige Entscheidungen

- **Playwright für webmailer**: webmailer.gmx.net ist same-process iframe → `frame.evaluate()` funktioniert für Shadow DOM Walk
- **CDP nur für OOPIF**: Email-Body lädt in `gmxnet.mailbody-ui.de` (cross-origin OOPIF) → `cdp.attach_to_iframe("mailbody-ui.de")` + `Runtime.evaluate`
- **`page.reload()` verboten**: Killt GMX Session (Navigation zu auth.gmx.net). Nur iframe-lokaler reload via CDP
- **`page.goto()` nur auf www.gmx.net**: Statische Landing Page. Ab navigator.gmx.net kein goto mehr (SPA!)
- **`return {{...}}` verboten**: Python interpretiert `{{}}` als Set mit Dict → `TypeError: unhashable type: 'dict'`. Immer einfache `{}` für Dicts

## OTP Flow (read_otp)

1. `_pw_connect(cdp_port)` → bevorzugt `bap.navigator.gmx.net/mail?sid=` Seiten
2. `_ensure_gmx_inbox()` → wenn nicht auf Inbox, www.gmx.net goto + "Zum Postfach" Klick + Consent-Handling
3. Webmailer iframe finden (webmailer.gmx.net)
4. JS Shadow DOM Walk: `querySelectorAll('*')` + `shadowRoot` Traversal + `findHost()` überspringt Shadow-Boundary
5. Klick auf `LIST-MAIL-ITEM` → Email öffnet in Detail-Ansicht
6. 5s warten → OOPIF `gmxnet.mailbody-ui.de` erscheint
7. CDP `attach_to_iframe("mailbody-ui.de")` → `Runtime.evaluate("document.body.innerText")` → regex nach Fireworks Verify URL

## open_gmx_email()

Dedizierte Funktion zum Öffnen einer Email (kein OTP, kein URL-Read):
```python
result = await gmx.open_gmx_email(sender_filter="fireworks", cdp_port=9222)
# → {"status": "success", "clicked": {"clicked": true, "tag": "list-mail-item"}}
```

CLI: `python tools/open_gmx_email.py --sender fireworks`

## Session Recovery

- Keine `page.goto()` / `page.reload()` auf navigator.gmx.net
- Session Check via CDP Targets (check_session)
- Cookie-Injektion via Playwright add_cookies() für Session-Wiederherstellung
- Master-Backup in `backup/session/gmx-cookies-master.json` (falls vorhanden)

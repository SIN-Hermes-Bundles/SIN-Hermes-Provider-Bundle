# gmx_service.py

GMX E-Mail Service für Alias-Rotation + OTP-Read (Playwright-native, V15.1 2026-05-30).

- **Alias-Rotation**: Playwright iframe-Interaktion via webmailer.settings frame. `_find_alias_row()` nutzt `div.table_body-row` statt `document.body.innerText`. `_delete_alias()` nutzt `div.table_body-row:has-text()` für Row-Selektion, Dialog-Handler vor Click, JS dispatchEvent Fallback, DOM-Dialog Bestätigung (Löschen/OK/Bestätigen/Ja/Entfernen). `_verify_alias()` prüft `div.table_body-row` statt `document.body.innerText`.
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

- **Playwright locator() für webmailer**: webmailer.gmx.net ist same-process iframe. `document.querySelectorAll()` findet NUR light-DOM Elemente (74), aber Playwright `locator()` durchdringt >2 Ebenen Shadow DOM nativ → findet `list-mail-item` (42 Elemente). **NICHT `frame.evaluate()` mit JS Walk verwenden**.
- **CDP nur für OOPIF**: Email-Body lädt in `gmxnet.mailbody-ui.de` (cross-origin OOPIF) → `cdp.attach_to_iframe("mailbody-ui.de")` + `Runtime.evaluate`
- **`page.reload()` verboten**: Killt GMX Session (Navigation zu auth.gmx.net). Nur iframe-lokaler reload via CDP
- **`page.goto()` nur auf www.gmx.net**: Statische Landing Page. Ab navigator.gmx.net kein goto mehr (SPA!)
- **`return {{...}}` verboten**: Python interpretiert `{{}}` als Set mit Dict → `TypeError: unhashable type: 'dict'`. Immer einfache `{}` für Dicts

## OTP Flow (read_otp)

1. `_pw_connect(cdp_port)` → bevorzugt `bap.navigator.gmx.net/mail?sid=` Seiten
2. `_ensure_gmx_inbox()` → wenn nicht auf Inbox, www.gmx.net goto + "Zum Postfach" Klick + Consent-Handling
3. Webmailer iframe finden (webmailer.gmx.net)
4. **Playwright locator(): `list-mail-item.list-mail-item--unread`** (pierced Shadow DOM nativ!)
5. **Filter**: `has_text=sender_filter` → nur Emails von fireworks
6. Klick auf erste unread Email → öffnet Detail-Ansicht
7. 5s warten → OOPIF `gmxnet.mailbody-ui.de` erscheint
8. CDP `attach_to_iframe("mailbody-ui.de")` → `Runtime.evaluate("document.body.innerText")` → regex nach Fireworks Verify URL
9. Fallback: webmailer frame body (nur wenn OOPIF nicht verfügbar)

## open_gmx_email()

Dedizierte Funktion zum Öffnen einer Email (kein OTP, kein URL-Read):
```python
result = await gmx.open_gmx_email(sender_filter="fireworks", cdp_port=9222)
# → {"status": "success", "clicked": True}
```

CLI: `python tools/open_gmx_email.py --sender fireworks`

## Session Recovery

- Keine `page.goto()` / `page.reload()` auf navigator.gmx.net
- Session Check via CDP Targets (check_session)
- Cookie-Injektion via Playwright add_cookies() für Session-Wiederherstellung
- Master-Backup in `backup/session/gmx-cookies-master.json` (falls vorhanden)

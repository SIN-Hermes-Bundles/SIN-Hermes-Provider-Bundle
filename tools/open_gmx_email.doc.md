# open_gmx_email.py

CLI Tool zum Öffnen einer Email im GMX Webmailer. Findet die Email anhand des Sender-Filters und klickt sie via `GmxService.open_gmx_email()`. Kein OTP — nur Öffnen.

## Berührt

- `gmx_service.py` — Nutzt `GmxService.open_gmx_email()` (Zeile 945)
- `~/.config/opencode/skills/gmx-email-open/SKILL.md` — Skill-Dokumentation

## Usage

```bash
python tools/open_gmx_email.py --sender fireworks
python tools/open_gmx_email.py --sender "no-reply@fireworks.ai"
python tools/open_gmx_email.py --sender "verify" --port 9222
```

## Flow

```
1. GmxService.open_gmx_email(sender_filter="fireworks", cdp_port=9222)
2. → _pw_connect() → GMX Inbox Page finden
3. → _ensure_gmx_inbox() → sicherstellen auf Inbox
4. → Webmailer iframe (webmailer.gmx.net) finden
5. → Playwright locator: list-mail-item (pierced Shadow DOM)
6. → Filter: has_text=sender_filter
7. → Klick auf erste unread Email
8. → Email öffnet in Detail-Ansicht
```

## Wird verwendet für

- Debugging: Email-Inhalt lesen ohne OTP zu extrahieren
- Testing: Session nach Cookie-Injektion validieren
- Manuelle Aktionen: Email öffnen wenn OTP nicht automatisch gefunden wurde

# cdp_client.py

Raw Chrome DevTools Protocol Client via WebSocket. Kein Playwright/Puppeteer — low-level CDP-Befehle für Sonderfälle: cross-origin iframes, Shadow DOM, OOPIFs.

## Berührt

- `gmx_service.py` — Nutzt CDP für OTP-Read aus webmailer iframe
- `browser_manager.py` — Browser Start/Stop

## Wichtige Entscheidungen

- Raw WebSocket statt Playwright: Playwright kann cross-origin iframes + Shadow DOM nicht penetrieren (CORS). CDP `Runtime.evaluate` läuft im Ziel-iframe-Kontext direkt
- `attach_to_iframe(url_prefix)` — Matcht iframe anhand URL, erstellt Execution Context, führt JS aus. Nur CDP-Methode umgeht CORS-Beschränkung

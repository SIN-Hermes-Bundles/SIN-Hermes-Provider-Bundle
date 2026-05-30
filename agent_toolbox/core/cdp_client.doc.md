# cdp_client.py

Raw Chrome DevTools Protocol Client via WebSocket. Kein Playwright/Puppeteer — low-level CDP-Befehle nur noch für OOPIFs (cross-origin iframes in separaten Prozessen). Webmailer (same-process iframe) wird via Playwright frame API bedient.

## Berührt

- `gmx_service.py` — Nutzt CDP für OOPIF-Zugriff auf `gmxnet.mailbody-ui.de` (Email Body nach Öffnen)
- `browser_manager.py` — Browser Start/Stop

## Wichtige Entscheidungen

- **CDP nur für OOPIFs**: Playwright `frame.evaluate()` funktioniert für same-process iframes (webmailer.gmx.net). CDP `attach_to_iframe()` + `Runtime.evaluate` nur noch nötig für cross-origin OOPIFs wie `gmxnet.mailbody-ui.de`
- `attach_to_iframe(url_prefix)` — Matcht OOPIF anhand URL, erstellt Execution Context, führt JS aus. Einzige Methode die CORS umgeht

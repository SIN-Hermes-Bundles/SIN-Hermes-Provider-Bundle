# gmx_service.py

GMX E-Mail Service für Alias-Rotation + OTP-Read. Playwright-native Navigation durch GMX Portal, iframe-interaktion für Alias CRUD, CDP-basiertes OTP-Reading aus cross-origin webmailer iframe mit Shadow DOM.

## Berührt

- `cdp_client.py` — CDP WebSocket-Kommunikation für OTP
- `fireworks_service.py` — übergibt Alias für Signup
- `browser_manager.py` — Browser-Lifecycle (start/stop)
- `tools/rotate.py` — Orchestriert Alias-Erstellung + Signup

## Config / Limits

- `MAX_OTP_RETRIES: 25` — Polls alle 8s = 200s max
- `GMX_FREEMAIL_ALIAS_LIMIT: 1` — Nur ein Alias gleichzeitig
- OTP liest aus `webmailer.gmx.net` cross-origin iframe (CORS-Problematik → CDP nötig)

## Wichtige Entscheidungen

- CDP statt Playwright für OTP: Playwright `frame.evaluate()` scheitert an cross-origin webmailer iframe + Shadow DOM. CDP `attach_to_iframe()` + `Runtime.evaluate` umgeht CORS
- `page.reload()` verboten: Killt GMX Session (Navigation zu auth.gmx.net). Nur iframe-lokaler reload via CDP

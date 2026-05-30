# cookie_manager.py

GMX Session-Cookie Management: Extrahieren, Speichern, Injizieren, Validieren. Legacy-System — aktuelle V15.1 nutzt Playwright direkt für Session-Management (kein Cookie-Manager nötig für Rotation).

## Berührt

- `agent_toolbox/api/routes/cookies.py` — Cookie Extract/Inject API Endpoints
- `tools/rotate.py` — historisch für Cookie-Injektion vor Rotation
- `data/gmx-cookies.json` — Persistierte Cookie-Datei

## Config / Limits

- **Storage Dir:** `./data/` (default)
- **Files:** `gmx-cookies.json`, `gmx-cookies-current.json`
- **Domain Filter:** Optional — z.B. "gmx" für nur GMX-Cookies
- **Cookie-Typen:** httpOnly, secure, session_cookies (expires=-1)

## Wichtige Entscheidungen

- **Injection ist DEPRECATED:** `POST /cookies/inject` wirft `RuntimeError` — Playwright-basierter Login in rotate.py hat Cookie-Injektion abgelöst
- **Extraction funktioniert noch:** `POST /cookies/extract` extrahiert Cookies via Playwright `context.cookies()`
- **Session-Prüfung nutzt `page.goto()`:** `verify_session()` navigiert zu `navigator.gmx.net/mail` — kann Session zerstören!
- **Singleton:** `get_cookie_manager()` — eine Instanz pro Prozess

## Flow

```python
# Extrahieren (funktioniert)
cm = get_cookie_manager()
cookies = cm.extract_cookies(page, domain_filter="gmx")
cm.save_cookies(cookies, "gmx-cookies.json")

# Injizieren (DEPRECATED — wirft RuntimeError)
cm.inject_cookies(context, cookies)

# Validieren (kann Session zerstören!)
is_valid = await cm.verify_session(page)
```

## Status

**Semi-deprecated.** Cookie-Extraktion funktioniert, aber Cookie-Injektion ist deaktiviert (wirft RuntimeError). Aktuell wird Playwright-native Session-Management in `gmx_service.py` und `tools/rotate.py` verwendet.

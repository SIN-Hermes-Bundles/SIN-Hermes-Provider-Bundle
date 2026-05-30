# cookies.py (Routes)

Cookie Management API Endpoints: Extract, Inject. FastAPI Router unter `/cookies/*`. Cookie-Injection ist DEPRECATED (Playwright-basierter Login hat sie abgelöst).

## Berührt

- `cookie_manager.py` — `get_cookie_manager()` Singleton
- `browser_manager.py` — `get_browser_manager()` für Page-Zugriff
- `schemas.py` — Cookie-Request/Response-Models

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| POST | `/cookies/extract` | Cookies aus Browser extrahieren + speichern |
| POST | `/cookies/inject` | Cookies in Browser injizieren (DEPRECATED) |

## Wichtige Entscheidungen

- **Extract funktioniert:** Extrahiert Cookies via Playwright `context.cookies()` + optionaler Domain-Filter
- **Inject ist DEPRECATED:** `POST /cookies/inject` wirft `RuntimeError` mit "Use Playwright-based login in rotate.py instead"
- **File-basiert:** Cookies werden als JSON in `./data/gmx-cookies.json` gespeichert
- **Stats:** Extract gibt Cookie-Statistiken zurück (domains, httpOnly, secure, session_cookies)

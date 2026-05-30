# rotate.py

Full Rotation Orchestrator: GMX Alias erstellen → Fireworks AI Signup → API Key generieren → Pool speichern. Playwright-native (kein CDP).

## Berührt

- `gmx_service.py` — `login()`, `rotate_alias()`, `read_otp()`
- `fireworks_service.py` — `signup_fireworks()`, `login_fireworks()`, `create_api_key()`
- `pool_manager.py` — `add_key()`

## Flow

```python
1. GmxService.login()            # Playwright GMX Login
2. GmxService.rotate_alias()     # Alias löschen + neu
3. signup_fireworks(alias, pw)   # Playwright Signup + OTP
4. login_result = login_fireworks(alias, pw)    # Playwright + CUA Login/Onboarding
5. create_api_key(key_name, page=login_result['page'], playwright=login_result['playwright'], browser=login_result['browser'])      # Playwright API Key (Session Reuse)
6. PoolManager.add_key()         # JSON speichern
```

## Session Reuse (Critical)
- `login_fireworks()` gibt jetzt `{'page': page, 'playwright': playwright, 'browser': browser, 'success': True}` zurück
- `create_api_key()` akzeptiert diese Session-Objekte und wiederverwendet sie statt neue Page zu erstellen
- **Why:** API Key Seite redirected zu `/login` wenn Session nicht gültig. Neue Page = keine Cookies = Login-Redirect.

## Limits

- Cycle Time: ~37s GMX + ~60s FW Signup + ~30s API Key = ~130s total

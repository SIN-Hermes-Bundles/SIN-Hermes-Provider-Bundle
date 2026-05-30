# fireworks_service.py

Fireworks AI Account-Management: Signup, Login, Onboarding, API Key Erstellung. Hybrid aus Playwright (Form-Interaktion) und CUA (React Checkboxen im Onboarding).

## Berührt

- `gmx_service.py` — Holt Alias + OTP für Signup
- `pool_manager.py` — Speichert neuen API-Key im Pool
- `cua_helper.py` — CUA Window Detection für Onboarding
- `tools/rotate.py` — Ruft signup → login → create_api_key

## Config / Limits

- `OTP_POLL_ATTEMPTS: 25` × 8s = 200s max
- Account Status: `partial` (unverified), `active`, `suspended`
- Suspended wenn $5 Credits aufgebraucht — Key dann `used` markieren

## Wichtige Entscheidungen

- Playwright + CUA Hybrid: Playwright für Form-fill (stabiler), CUA für React-Checkboxen (Playwright hat keine AX-IDs in Custom React Components)
- Onboarding-Fallback: Wenn CUA fehlschlägt, Playwright-eigener Onboarding-Pfad

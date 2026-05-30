# fireworks_service.py

Fireworks AI Account-Management: Signup, Login, Onboarding, API Key Erstellung. Hybrid aus Playwright (Form-Interaktion) und CUA (nur für AXTextField).

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

- **CUA NUR für Names (AXTextField):** `get_window_state` zeigt Chrome UI (Tabs, Bookmarks), NICHT Web-Content. Nur AXTextField-Elemente sind im Chrome-AX-Tree sichtbar. Checkbox/Button existieren dort nicht → müssen via Playwright geklickt werden.
- **Checkbox-Strategie:** 1) `input[type="checkbox"]` mit aria-label "agree", 2) `label` mit textContent "i agree", 3) Fallback `label:has-text("Terms")` (matcht sonst Terms-of-Service-Links!).
- **Onboarding-Pfad:** Immer Playwright für Checkbox/Continue/Submit. CUA nur für type_text (CGEvent-Tastendrücke) auf React-Textfelder, die Playwrights `type()` nicht verarbeitet.
- **Erkannt (2026-05-30):** CUA `get_window_state` findet Chrome-AX-Tree (Tabs, Bookmarks, Toolbar). Web-Content (Canvas/Shadow-DOM) ist nicht sichtbar.

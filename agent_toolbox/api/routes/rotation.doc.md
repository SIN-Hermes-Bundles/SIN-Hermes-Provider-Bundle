# rotation.py (Routes)

Rotation Orchestrator API: Startet `tools/rotate.py` als Subprocess mit Config-Manager Credentials. Dashboard-kompatibel — teilt Chrome in 2 Fenster (Dashboard + Rotation nebeneinander).

## Berührt

- `tools/rotate.py` — Wird als Subprocess aufgerufen
- `config_manager.py` — `get_config()` für GMX/FW Credentials
- `schemas.py` — `RotationRequest` + `RotationResponse` Pydantic Models
- Dashboard — Button "Neuen Key generieren" → `POST /rotation/full`

## Endpoints

| Methode | Route | Zweck |
|--------|-------|-------|
| POST | `/rotation/full` | Komplette Account-Rotation (GMX → FW → Key) |

## Config / Limits

- **Chrome Split:** Fenster 1 (links, 960px) = Dashboard, Fenster 2 (rechts, 960px) = Rotation
- **CDP Port:** 9222 (hardcoded)
- **Credentials:** Via Config Manager (nicht hardcoded!)
- **Output Parsing:** Regex aus stdout: `✅ GMX Alias:` + `✅ API Key:`

## Wichtige Entscheidungen

- **Subprocess nicht API-Calls:** Rotation ruft `python3 tools/rotate.py` als Subprocess — nicht via interne Funktionsaufrufe. Grund: Isolation, Logging, Error-Handling.
- **AppleScript Fenster-Management:** Chrome wird via `osascript` in 2 gleich große Fenster geteilt (kein externes Fenster-Management-Tool)
- **Live-Output Parsing:** `proc.stdout` wird Zeile-für-Zeile geparst — kein vollständiges read() am Ende
- **Partial Status:** Wenn GMX funktioniert aber API Key nicht → `partial` status
- **`fireworks_account = gmx_alias`:** Die registrierte Fireworks-Email ist immer die GMX-Alias-Email

## Flow

```
POST /rotation/full
  → AppleScript: Chrome Fenster teilen
  → Config laden (get_config())
  → Subprocess: python3 tools/rotate.py --gmx-email ... --password ... --cdp-port 9222
  → stdout zeilenweise parsen:
      "✅ GMX Alias:" → gmx_alias
      "✅ API Key:" → api_key
      "Login + Onboarding OK" → fireworks_login_success
  → Status bestimmen: success | partial | failed
  → RotationResponse zurück
```

## Fehlerbehandlung

| Situation | Status | Response |
|-----------|--------|----------|
| GMX + FW + Key | success | alle Felder gefüllt |
| GMX + FW, kein Key | partial | gmx_alias + fireworks_account, kein api_key |
| Nur GMX | partial | nur gmx_alias |
| Subprocess crash | error | error=Exception message |

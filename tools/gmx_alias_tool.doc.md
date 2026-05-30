# gmx_alias_tool.py

Interaktives CLI-Tool für GMX Alias-Operationen. READ-ONLY VERIFIED — Änderungen verboten. Verwendet die verifizierten GmxService-Methoden direkt.

## Berührt

- `gmx_service.py` — Alle Operationen delegieren an `GmxService.create_alias()`, `rotate_alias()`, `delete_existing_alias()`, `check_session()`
- `agent_toolbox/api/routes/gmx.py` — API-Alternative zu diesem CLI-Tool

## Commands

| Command | Funktion |
|---------|----------|
| `status` | GMX Session prüfen + aktuellen Alias anzeigen |
| `check` | Detaillierte Session-Validierung (Homepage → Email → Inbox) |
| `rotate [name]` | Alias rotieren (delete + create). Name optional. |
| `create [name]` | Nur Alias erstellen. Name optional (sonst auto-generiert). |
| `delete` | Alias löschen mit Bestätigung |

## Usage

```bash
python tools/gmx_alias_tool.py status
python tools/gmx_alias_tool.py rotate
python tools/gmx_alias_tool.py rotate my-custom-alias
python tools/gmx_alias_tool.py create my-alias
python tools/gmx_alias_tool.py delete
```

## Wichtige Entscheidungen

- **READ-ONLY VERIFIED:** Dieses Tool wurde getestet und funktioniert. NIEMALS ändern.
- **Kein Playwright:** Direkte GmxService-CDP-Aufrufe
- **API Alternative:** `curl -X POST http://localhost:8000/gmx/alias/rotate` ist die bevorzugte Methode
- **CDP Port:** Hardcoded 9222

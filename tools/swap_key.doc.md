# swap_key.py

CLI-Tool für Auto-Key-Swap bei Fireworks Rate-Limit. Reported den bad key via Pool-API und updated OpenCode's `auth.json` mit dem neuen Key. Kein Session-Neustart nötig.

## Berührt

- `agent_toolbox/api/routes/pool.py` — `POST /pool/report` für Key-Swap
- `~/.local/share/opencode/auth.json` — OpenCode Auth-Datei
- `proxy/server.py` — Proxy macht Key-Swap automatisch (dieses Tool ist für CLI-Nutzer)

## Usage

```bash
python tools/swap_key.py              # Auto-detect bad key from auth.json
python tools/swap_key.py fw_xxx       # Specific key to report
```

## Flow

```
1. Lies bad_key aus auth.json (oder CLI-Argument)
2. POST /pool/report {"api_key": bad_key}
   → Pool markiert bad_key als used + leaset neuen Key
3. Schreibe neuen Key nach ~/.local/share/opencode/auth.json
4. Fertig — OpenCode liest auth.json bei jedem API-Call
```

## Wichtige Entscheidungen

- **Kein Session-Neustart:** OpenCode read auth.json live — kein Restart nötig
- **Pool muss verfügbar sein:** Wenn keine Keys im Pool → Fehler "Run rotation!"
- **Auth-File-Format:** `{"fireworks": "fw_xxx"}`
- **Proxy macht das automatisch:** Für Proxy-Nutzer ist dieses Tool nicht nötig

# browser_manager.py

Singleton für Chrome Browser Lifecycle Management. Startet/Stoppt Chrome mit ORIGINAL Profile 901 (KEINE Kopie!). Verwaltet CDP Port 9222 und prüft ob Chrome bereits läuft. Wird von ALLEN Route-Handlern (gmx, fireworks, cookies, browser) als Prerequisite verwendet.

## Berührt

- `agent_toolbox/api/routes/*` — `_require_browser()` in gmx + fireworks Routen
- `agent_toolbox/start_toolbox.py` — Shutdown-Cleanup + Health-Check
- `agent_toolbox/core/gmx_service.py` — indirekt via CDP Port
- `agent_toolbox/core/fireworks_service.py` — indirekt via CDP Port

## Config / Limits

- **Chrome Binary:** `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- **User Data Dir:** `/Users/jeremy/Library/Application Support/Google Chrome`
- **Profile:** `Profile 901`
- **CDP Port:** `9222`
- **Flags:** `--no-first-run --no-default-browser-check --remote-allow-origins=*`

## 🔴 ABSOLUTE REGELN (NIEMALS VERLETZEN)

1. **NIEMALS Profil kopieren:** Chrome-Cookies sind via macOS Keychain an ORIGINAL Pfad gebunden → Kopie = Session tot
2. **NIEMALS `pkill -9`:** Zerstört unflushed SQLite → Session permanent kaputt
3. **NIEMALS `--user-data-dir=/tmp/...`:** Falscher Pfad → Keychain-Mismatch → Cookies unlesbar
4. **NIEMALS Chrome neustarten wenn bereits läuft:** `start()` prüft zuerst und verbindet nur

## Flow

```
BrowserManager ist Singleton — get_browser_manager() immer gleiche Instanz:

start():
  1. _is_chrome_already_running() → GET :9222/json/version
  2. Wenn bereits läuft → "connected" (kein Neustart!)
  3. Wenn nicht → _launch_chrome_original_profile()
     → nohup Chrome mit Profile 901 + CDP 9222
  4. Return {status, cdp_port, profile, startup_time}

stop():
  1. SIGTERM an Chrome Prozess → wait 5s
  2. Falls nicht reagiert → SIGKILL (last resort)
  3. Return {status, cleanup_actions}
```

## Veralteter Code

- **Profile kopieren:** Alter Code kopierte Profile 901 nach `/tmp/` → GELÖSCHT
- **Temp Profile Dir:** Alte Implementierung nutzte `temp_profile_dir` → Weg
- **Headless-Mode:** `--headless=new` Flag existiert aber wird nie verwendet (braucht GUI für CUA)

# INSTALL.md — SINator Fireworks AI Backend

SINator Backend installieren: Python deps, Playwright, macOS LaunchAgents, Pool-Proxy.

---

## Prerequisites

- macOS 14+
- Python 3.11+ (`python3 --version`)
- Homebrew (`/opt/homebrew/bin/python3`)

## 1. Repo klonen

```bash
cd ~/dev
git clone git@github.com:SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle.git SINator-fireworksai
cd SINator-fireworksai
```

## 2. Python Dependencies

```bash
pip3 install -r agent_toolbox/requirements.txt
playwright install chromium
```

## 3. Konfigurieren

```bash
cp agent_toolbox/.env.example .env
```

`.env` anpassen:

| Variable | Wert |
|----------|------|
| `GMX_EMAIL` | GMX Login-Email |
| `GMX_PASSWORD` | GMX Passwort |
| `FIREWORKS_PASSWORD` | Passwort für neue Fireworks-Accounts |
| `CDP_PORT` | `9222` (wird nicht mehr genutzt — Playwright launch()) |
| `HEADLESS` | `false` (Browser sichtbar zum Debuggen) |

## 4. Backend starten

```bash
python3 agent_toolbox/start_toolbox.py
```

Swagger UI: http://localhost:8000/docs

## 5. Pool-Proxy starten (10 Proxys + Router)

```bash
bash proxy/start-multi.sh
```

Startet:
- Pool-Router auf `:9998` (auto-failover)
- 10 Proxy-Instanzen auf `:8888`-`:8897`

Verify:

```bash
curl http://localhost:9998/health
curl http://localhost:9998/v1/models
```

## 6. Ersten Key rotieren

```bash
python3 tools/rotate.py
```

ODER mit automatischem Pool-Save:

```bash
python3 tools/rotate.py --save
```

ODER Batch (z.B. 10 Keys):

```bash
python3 tools/batch_rotate.py --count 10
```

## 7. macOS LaunchAgents (Auto-Start)

```bash
python3 tools/manage_services.sh install   # Alle Services installieren
python3 tools/manage_services.sh start     # Alle Services starten
python3 tools/manage_services.sh status    # Status prüfen
```

| Service | Port | LaunchAgent |
|---------|------|-------------|
| Backend | :8000 | `com.sinator.backend` |
| Pool-Router | :9998 | `com.sinator.pool-router` |
| Pool-Proxy | :8888-:8897 | `com.sinator.pool-proxy-{port}` |
| Pages | :8040 | `com.sinator.pages` |

## 8. Zugriff

| Zweck | URL |
|-------|-----|
| **OpenAI API** | `https://sinatorpool-router.delqhi.com/inference/v1` |
| Backend Health | `http://localhost:8000/health` |
| Pool Stats | `http://localhost:8000/api/v1/pool/stats` |
| Swagger UI | `http://localhost:8000/docs` |
| Pool-Router | `http://localhost:9998/health` |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `playwright install` failed | `playwright install --with-deps chromium` |
| Port 8000 belegt | `lsof -i :8000` → `kill <PID>` |
| Proxy 429/412 | Pool-Router swapt automatisch — nächster Proxy |
| GMX Alias Create scheitert | Retry in rotate.py (3 Versuche) |
| Alle Keys suspended | `python3 tools/rotate.py --save` für neue Keys |

---

*Stand: 2026-05-31 | V15.4*

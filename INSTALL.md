# SINator Fireworks AI — Installation

*Prozedurale Schritt-für-Schritt-Anleitung. Jeder Schritt endet mit einer Verifikation.*

---

## 1. Voraussetzungen

### 1.1 Python 3.11+

```bash
python3 --version
# ✅ MUSS "Python 3.11.x" oder höher anzeigen
# ❌ "command not found" → brew install python3
```

### 1.2 Google Chrome

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
# ✅ MUSS "Google Chrome xxx" anzeigen
# ❌ "No such file or directory" → Chrome installieren
```

### 1.3 Homebrew (empfohlen)

```bash
which brew
# ✅ `/opt/homebrew/bin/brew` oder `/usr/local/bin/brew`
# ❌ "not found" → /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 1.4 Hermes CLI (optional — nur für Hermes-Nutzung)

```bash
which hermes
# ✅ "/usr/local/bin/hermes" oder ähnlich
# ❌ → https://hermes.ai/docs/install
```

### 1.5 Fireworks AI API Key

```bash
echo "${FIREWORKS_AI_API_KEY}"
# ✅ Zeigt einen Key (beginnt mit "fw_..." oder "fir_...")
# ❌ leer → aus Pool holen (siehe Schritt 8)
```

---

## 2. Repository klonen

```bash
git clone https://github.com/SIN-Rotator/SINator-FireworksAI ~/dev/SINator-fireworksai
cd ~/dev/SINator-fireworksai

# ✅ Du bist jetzt im Ordner ~/dev/SINator-fireworksai
# ❌ "fatal: could not create work tree" → ~/dev existiert? `mkdir -p ~/dev`
```

---

## 3. Python Dependencies installieren

```bash
pip3 install fastapi uvicorn httpx playwright aiohttp

# ✅ Keine Fehlermeldung
# ❌ "externally-managed-environment" → pipx oder venv verwenden:
#    python3 -m venv .venv && source .venv/bin/activate && pip3 install ...
```

```bash
python3 -m playwright install chromium

# ✅ "Chromium downloaded to ..."
# ❌ Fehler → `brew install playwright` oder `npx playwright install chromium`
```

---

## 4. Backend starten (Port 8000)

```bash
python3 agent_toolbox/start_toolbox.py
# → Startet Uvicorn auf http://0.0.0.0:8000
```

**In einem zweiten Terminal — Verifikation:**

```bash
curl http://localhost:8000/health
# ✅ {"server":"ok","chrome":false,"cua":false,"version":"8.0.0"}
# ❌ "Connection refused" → Backend läuft nicht. `tail -20 /tmp/sinator-backend.log`
```

```bash
curl http://localhost:8000
# ✅ {"service":"SINator Agent Toolbox","status":"running","docs":"/docs"}
```

---

## 5. Chrome starten (GMX Session)

GMX erfordert Chrome mit **Profile 73** (simoneschulze) und CDP auf Port 9222.

```bash
# Chrome hard kill + Neustart mit CDP:
pkill -9 -f "Google Chrome" 2>/dev/null; sleep 2

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir="/Users/simoneschulze/Library/Application Support/Google Chrome" \
  --profile-directory="Profile 73" \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check &

sleep 5
curl -s http://127.0.0.1:9222/json/version
# ✅ `"Browser": "Chrome/..."` — CDP ist ready
# ❌ "Connection refused" → Chrome nicht gestartet. `tail -20 /tmp/chrome_sinator.log`
```

---

## 6. Proxys + Pool-Router starten (8888-8897, 9998)

### 6.1 Quick-Start (alle auf einmal)

```bash
bash proxy/start-multi.sh
# ✅ "10 Proxys + Router gestartet"
# ❌ "Address already in use" → `lsof -ti :8888 | xargs kill -9` und erneut versuchen
```

### 6.2 Verifikation

```bash
# Router:
curl http://localhost:9998/health
# ✅ {"status":"ok","pools":{...}}

# Proxys (stichprobe):
curl http://localhost:8888/health
# ✅ {"status":"ok","key_status":"leased","model":"..."}
```

### 6.3 launchd-Autostart (optional — für dauerhaften Betrieb)

```bash
./tools/manage_services.sh install
./tools/manage_services.sh start
./tools/manage_services.sh status
# ✅ Alle Services grün (backend, pool-router, pool-proxy-8888..8897)
# ❌ Ein Service rot → `launchctl list | grep com.sinator` + Logs prüfen
```

---

## 7. GMX Credentials konfigurieren

```bash
# Via Dashboard:
open http://localhost:8000/dashboard
# → Setup → GMX Email + GMX Passwort + Fireworks Passwort eintragen

# Oder via API:
curl -X POST http://localhost:8000/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "gmx_email": "deine-email@gmx.de",
    "gmx_password": "dein-gmx-passwort",
    "password": "dein-fireworks-passwort"
  }'
# ✅ {"status":"success"}
# ❌ 401 → Auth-Token fehlt. Aus Backend-Log kopieren oder SINATOR_AUTH_TOKEN setzen.
```

**Config prüfen:**

```bash
curl http://localhost:8000/api/v1/config
# ✅ {"status":"success","data":{"gmx_email":"...","password":"...","gmx_password":"..."}}
```

---

## 8. Key Pool füllen (Rotation)

### 8.1 Einmalige Rotation

```bash
python3 tools/rotate.py
# ✅ "✅ Rotation complete — API Key added to pool"
# ❌ "GMX session dead" → Session Recovery (siehe AGENTS.md)
# ❌ "CAPTCHA" → Session inkorrekt. Master-Backup wiederherstellen.
```

### 8.2 Pool-Status prüfen

```bash
curl http://localhost:8000/api/v1/pool/stats
# ✅ {"status":"success","total":219,"available":95,"used":10,"suspended":114}
```

### 8.3 Automatische Rotation (alle 90s)

```bash
python3 tools/batch_rotate.py
# → Läuft durch bis Pool voll ist oder Credentials limit erreicht
```

---

## 9. Public Tunnel (optional — Remote-Zugriff)

```bash
# Einmalig starten:
./tools/start_tunnel.sh
# ✅ "Public URL: https://xxx.trycloudflare.com"

# Als launchd-Dienst installieren (Autostart):
./tools/start_tunnel.sh --install

# Status prüfen:
./tools/start_tunnel.sh --status
# ✅ "Tunnel is running — URL: https://xxx.trycloudflare.com"
# ❌ "Tunnel is not running" → cloudflared installieren: `brew install cloudflared`
```

---

## 10. Client konfigurieren

### 10.1 Hermes

```bash
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"
# ✅ "Added custom:fireworks"

# Config prüfen:
cat ~/.hermes/config.yaml | grep -A4 "custom:fireworks"
# ✅ MUSS enthalten:
#   base_url: https://sinatorpool-router.delqhi.com/inference/v1
#   (oder http://localhost:9998/inference/v1 für lokale Nutzung)
```

### 10.2 OpenCode

```json
{
  "provider": {
    "fireworks-ai": {
      "options": {
        "baseURL": "https://sinatorpool-router.delqhi.com/inference/v1",
        "apiKey": "dein-api-key"
      }
    }
  }
}
```

### 10.3 Python (OpenAI SDK)

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://sinatorpool-router.delqhi.com/inference/v1",
    api_key="dein-api-key",
)
models = client.models.list()
# ✅ Sollte 12+ Modelle zurückgeben
```

---

## 11. Verifikation — alles läuft?

Ein Befehl, der das gesamte System prüft:

```bash
python3 -c "
import urllib.request, json

ok, fail = [], []

# Backend
try:
    r = urllib.request.urlopen('http://localhost:8000/health', timeout=3)
    data = json.loads(r.read())
    ok.append(f'Backend :8000 — {data[\"server\"]}')
except Exception as e:
    fail.append(f'Backend :8000 — {e}')

# Router
try:
    r = urllib.request.urlopen('http://localhost:9998/health', timeout=3)
    ok.append('Router :9998 — ok')
except Exception as e:
    fail.append(f'Router :9998 — {e}')

# Proxys (Stichprobe :8888)
try:
    r = urllib.request.urlopen('http://localhost:8888/health', timeout=3)
    ok.append('Proxy :8888 — ok')
except Exception as e:
    fail.append(f'Proxy :8888 — {e}')

# Pool
try:
    r = urllib.request.urlopen('http://localhost:8000/api/v1/pool/stats', timeout=3)
    data = json.loads(r.read())
    ok.append(f'Pool — {data.get(\"available\", \"?\")} Keys verfügbar')
except Exception as e:
    fail.append(f'Pool — {e}')

print('✅ Alles OK' if not fail else '❌ Fehler:')
for m in ok: print(f'  ✅ {m}')
for m in fail: print(f'  ❌ {m}')
"
```

**Erwartete Ausgabe:**
```
✅ Alles OK
  ✅ Backend :8000 — ok
  ✅ Router :9998 — ok
  ✅ Proxy :8888 — ok
  ✅ Pool — 95 Keys verfügbar
```

---

## 12. Fehlerbehebung

| Problem | Ursache | Lösung |
|---------|---------|--------|
| `Connection refused` auf `:8000` | Backend läuft nicht | `tail -20 /tmp/sinator-backend.log` |
| `Connection refused` auf `:9222` | Chrome ohne CDP gestartet | Schritt 5 wiederholen |
| GMX Session tot | Cookie abgelaufen | Master-Backup wiederherstellen (AGENTS.md) |
| `409 Conflict` bei Alias | Alias existiert bereits | `DELETE` vor `CREATE` — macht `rotate.py` automatisch |
| `412 Account suspended` | Spending Limit erreicht | Key ist tot → Proxy swappt automatisch |
| Keine Keys im Pool | Noch nie rotiert | `python3 tools/rotate.py` |
| `ModuleNotFoundError` | Deps nicht installiert | `pip3 install -r requirements.txt` (falls vorhanden) |

---

*Stand: 2026-05-29 | V14 | Playwright-native*

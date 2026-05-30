# SIN-Hermes-Provider-Bundle

Fireworks AI Pool-Konfiguration für OpenCode CLI und Hermes.

**Base URL:** `https://sinatorpool-router.delqhi.com/inference/v1`

**5 Reasoning-Modelle:** deepseek-v4-pro, glm-5p1, kimi-k2p6, qwen3p6-plus, minimax-m2p7 — jedes mit off/low/medium/high/max Thinking-Varianten.

**Auto-Failover:** 413/429/412/5xx → automatisch nächster Proxy. Du merkst nichts davon.

---

## Installieren

### Copy & Paste (schnellste Option)

```bash
mkdir -p ~/.config/opencode
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json -o ~/.config/opencode/opencode.json
```

Danach `apiKey` in der Datei ersetzen (`fw_DEIN_KEY` → dein echter Key).

### OpenCode CLI (One-Liner)

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_DEIN_KEY
```

Das schreibt `~/.config/opencode/opencode.json` — fügt Fireworks Provider + 5 Reasoning-Modelle hinzu. Bestehende Settings bleiben erhalten.

### OpenCode CLI — Config kaputt? Repair

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash
```

Erkennt ob `opencode.json` broken JSON ist oder nur der Provider fehlt. Bewahrt alles was geht, fügt Fireworks Provider + alle 5 Modelle hinzu.

### Hermes

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/config/fireworks-router.yaml -o ~/.hermes/config.yaml
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"
```

---

## Nutzen

### OpenCode CLI

```bash
opencode chat                                          # default: deepseek-v4-pro
opencode chat --model deepseek-v4-pro --variant high   # 64000 thinking tokens
opencode chat --model kimi-k2p6 --variant max           # 64000 thinking tokens + vision
opencode chat --model glm-5p1 --variant off             # kein thinking
```

### Varianten

| Variant | Thinking | Typisch für |
|---------|----------|-------------|
| `off` | disabled | Schnelle Antworten, kein Reasoning |
| `low` | 4000 tokens | Leichtes Reasoning |
| `medium` | 16000 tokens | Standard |
| `high` | 32000-64000 tokens | Komplexe Aufgaben |
| `max` | 64000-128000 tokens | Maximales Reasoning |

### Modelle

| Modell | ID | Thinking Default | Vision | Context |
|--------|----|-------------------|--------|---------|
| DeepSeek V4 Pro | `fireworks/deepseek-v4-pro` | 64000 | nein | 1M |
| GLM 5.1 | `fireworks/glm-5p1` | 32000 | nein | 200K |
| Kimi K2.6 | `fireworks/kimi-k2p6` | 32000 | ja | 262K |
| Qwen3.6 Plus | `accounts/fireworks/models/qwen3p6-plus` | 32000 | ja | 131K |
| MiniMax M2.7 | `fireworks/minimax-m2p7` | 32000 | nein | 196K |

### Python / curl / beliebiger OpenAI-Client

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://sinatorpool-router.delqhi.com/inference/v1",
    api_key="fw_DEIN_KEY",
)
resp = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[{"role": "user", "content": "Hallo"}],
)
```

```bash
curl https://sinatorpool-router.delqhi.com/inference/v1/models \
  -H "Authorization: Bearer fw_DEIN_KEY"
```

---

## Was im Repo ist

| Datei | Zweck |
|-------|-------|
| `opencode-config-install.sh` | One-Liner Installer für OpenCode CLI |
| `opencode-config-repair.sh` | Emergency Repair für broken `opencode.json` |
| `config/fireworks-router.yaml` | Hermes Config (remote Pool-Router) |
| `config/fireworks-pool1.yaml` | Hermes Config (Pool 1) |
| `config/fireworks-pool2.yaml` | Hermes Config (Pool 2) |
| `config/fireworks-pool3.yaml` | Hermes Config (Pool 3) |
| `install.sh` | Full Hermes-Backend Installer (Pool-Router + 10 Proxys + launchd) |
| `tests/test_opencode_config.py` | Test-Suite für Install/Repair-Scripts (17 Tests) |

---

## Backend / Rotator

Das Backend (Key-Rotation, Proxy-Server, Browser-Automation) ist in [SIN-Rotator/SINator-FireworksAI](https://github.com/SIN-Rotator/SINator-FireworksAI).

---

*Stand: 2026-05-31 | 234 Keys | Pool-Router: sinatorpool-router.delqhi.com*

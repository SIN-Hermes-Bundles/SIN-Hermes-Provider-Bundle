# SIN-Hermes-Provider-Bundle

Fireworks AI Pool-Konfiguration für OpenCode CLI — 12 Modelle mit temperatur 0.

**Base URL:** `https://sinatorpool-router.delqhi.com/inference/v1`
**Auto-Failover:** 413/429/412/5xx → nächster Proxy. Du merkst nichts.

---

## Installieren

### Copy & Paste (schnellste)

```bash
mkdir -p ~/.config/opencode
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json -o ~/.config/opencode/opencode.json
```

Danach `fw_DEIN_KEY` durch deinen echten API-Key ersetzen.

### One-Liner Installer

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_DEIN_KEY
```

Bestehende Settings bleiben erhalten. Fireworks Provider + 12 Modelle werden hinzugefügt.

### Config kaputt? Repair

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash
```

Erkennt broken JSON oder fehlenden Provider. Bewahrt was geht, fügt Fireworks + 12 Modelle hinzu.

---

## Nutzen

```bash
opencode chat                                           # default: deepseek-v4-pro
opencode chat --model deepseek-v4-pro --variant high    # 64000 thinking tokens
opencode chat --model kimi-k2p6 --variant max            # 64000 thinking tokens + vision
opencode chat --model gpt-oss-120b                       # kein thinking, deterministisch
opencode chat --model glm-5p1 --variant off              # kein thinking
```

### Varianten

| Variant | Thinking | Typisch für |
|---------|----------|-------------|
| `off` | disabled | Schnelle Antworten, kein Reasoning |
| `low` | 4000 tokens | Leichtes Reasoning |
| `medium` | 16000 tokens | Standard |
| `high` | 32000-64000 tokens | Komplexe Aufgaben |
| `max` | 64000-65536 tokens | Maximales Reasoning |

### Modelle

| Modell | ID | Thinking | Vision | Context |
|--------|----|----------|--------|---------|
| DeepSeek V4 Pro | `fireworks/deepseek-v4-pro` | 64000 | nein | 1M |
| DeepSeek V4 Flash | `accounts/fireworks/models/deepseek-v4-flash` | 32000 | nein | 1M |
| GLM 5.1 | `fireworks/glm-5p1` | 32000 | nein | 202K |
| GLM 5.1 Fast | `accounts/fireworks/routers/glm-5p1-fast` | 32000 | nein | 202K |
| Kimi K2.5 | `accounts/fireworks/models/kimi-k2p5` | 32000 | ja | 262K |
| Kimi K2.6 | `fireworks/kimi-k2p6` | 32000 | ja | 262K |
| Kimi K2.6 Turbo | `accounts/fireworks/routers/kimi-k2p6-turbo` | 32000 | ja | 262K |
| Qwen3.6 Plus | `accounts/fireworks/models/qwen3p6-plus` | 32000 | ja | 131K |
| MiniMax M2.5 | `accounts/fireworks/models/minimax-m2p5` | 32000 | nein | 196K |
| MiniMax M2.7 | `fireworks/minimax-m2p7` | 32000 | nein | 196K |
| GPT-OSS 120B | `accounts/fireworks/models/gpt-oss-120b` | — | nein | 131K |
| GPT-OSS 20B | `accounts/fireworks/models/gpt-oss-20b` | — | nein | 131K |

### Python / curl

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
| `opencode.json` | Provider-Konfiguration (617 Zeilen, Single Source of Truth) |
| `config.example.json` | Minimal-Beispiel der Config-Struktur (1 Modell) |
| `opencode-config-install.sh` | One-Liner Installer für OpenCode CLI |
| `opencode-config-repair.sh` | Emergency Repair für broken `opencode.json` |
| `INSTALL.md` | Detaillierte Install-Optionen + Troubleshooting |
| `requirements.txt` | Python-Deps für Tests (`pytest`) |
| `tests/test_opencode_config.py` | Test-Suite (19 Tests, 18 passed) |

---

*Stand: 2026-05-31 | Pool: 234 Keys | Pool-Router: sinatorpool-router.delqhi.com*

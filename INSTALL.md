# INSTALL.md — SIN-Hermes-Provider-Bundle

## Prerequisites

- macOS (Tested on macOS 14+)
- `bash` shell
- `curl` installed
- Hermes Agent (`pip install hermes-agent`)
- `launchctl` (macOS service management)

## Installation

### Quick Start (One-Command)

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/install.sh | bash
```

### Manual Step-by-Step

```bash
# 1. Clone repository
cd ~/dev
git clone https://github.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle.git
cd SIN-Hermes-Provider-Bundle

# 2. Run installer
./install.sh
```

## What Gets Installed

| Component | Purpose | Location |
|-----------|---------|----------|
| Pool Router | HTTP proxy with auto-failover | `~/.hermes/scripts/pool-router.py` |
| Config | Fireworks AI routing config | `~/.hermes/config.yaml` |
| 412 Patch | Retry on 412 PRECONDITION_FAILED | `~/.hermes/hermes-agent/agent/error_classifier.py` |
| UA-Spoof | Disable retries + User-Agent spoof | `~/.hermes/hermes-agent/_ua_patch.py` |
| V15 Patches | Progressive Tool Loading (7 files) | `~/.hermes/hermes-agent/` |
| Auto-Start | launchd service for router | `~/Library/LaunchAgents/com.sinator.pool-router.plist` |

## Verification

```bash
# 1. Check Pool Router (via public endpoint)
curl -s https://sinatorpool-router.delqhi.com/inference/v1/models | python3 -m json.tool | head -20
# → Expected: {"object": "list", "data": [{"id": "accounts/fireworks/models/deepseek-v4-pro", ...}]}

# 2. Check Auto-Start Service
launchctl list | grep com.sinator.pool-router
# → Expected: PID + Status

# 3. Check Hermes Config
grep "provider" ~/.hermes/config.yaml | head -5
# → Expected: provider: custom:fireworks

# 4. Check Patches
ls -la ~/.hermes/hermes-agent/tools/tool_search.py
# → Expected: File exists

# 5. Test API Key (optional)
curl -s -X POST https://sinatorpool-router.delqhi.com/inference/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FIREWORKS_AI_API_KEY" \
  -d '{"model":"accounts/fireworks/models/deepseek-v4-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

## Service Management

```bash
# Stop router
launchctl unload ~/Library/LaunchAgents/com.sinator.pool-router.plist

# Start router
launchctl load ~/Library/LaunchAgents/com.sinator.pool-router.plist

# Check status
pgrep -f pool-router.py

# View logs
tail -f ~/.hermes/logs/pool-router.log
```

## Post-Install

### Hermes (Terminal)

```bash
# Add Fireworks API key
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"

# Verify provider
hermes model

# Test chat
hermes chat -Q -q "say hello"
```

### OpenCode CLI (One-Liner)

Für OpenCode CLI mit Reasoning-Configs (5 Modelle, 5 Varianten):

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash
```

Mit API Key:
```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_xxx
```

Installiert:
- `provider.fireworks-ai` in `~/.config/opencode/opencode.json`
- 5 Reasoning-Modelle (deepseek-v4-pro, glm-5p1, kimi-k2p6, qwen3p6-plus, minimax-m2p7)
- Varianten: `off` / `low` / `medium` / `high` / `max`
- Base URL: `https://sinatorpool-router.delqhi.com/inference/v1`

## Troubleshooting

### Pool Router not responding
```bash
# Check if running
pgrep -f pool-router.py

# Restart manually
python3 ~/.hermes/scripts/pool-router.py &

# Check logs
tail -20 ~/.hermes/logs/pool-router.log
```

### Patches not applied
```bash
# Re-apply patches
cd ~/.hermes/hermes-agent
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/patches/error_classifier_412.patch | git apply
```

### Config missing
```bash
# Reset config
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/config/fireworks-router.yaml -o ~/.hermes/config.yaml
```

### OpenCode Reasoning-Configs fehlen nach One-Liner

Falls der One-Liner keine `thinking` / `variants` in `~/.config/opencode/opencode.json` erstellt hat:

```bash
# Manuell Reasoning-Configs hinzufügen
python3 << 'EOF'
import json
import os

config_path = os.path.expanduser("~/.config/opencode/opencode.json")

with open(config_path, 'r') as f:
    cfg = json.load(f)

# Fireworks Provider mit Reasoning
provider = {
    "npm": "@ai-sdk/fireworks",
    "name": "Fireworks AI",
    "models": {
        "deepseek-v4-pro": {
            "id": "fireworks/deepseek-v4-pro",
            "name": "DeepSeek V4 Pro (SIN)",
            "options": {
                "thinking": {"type": "enabled", "budgetTokens": 64000}
            },
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 128000}}
            },
            "limit": {"context": 1048576, "output": 65536}
        },
        "glm-5p1": {
            "id": "fireworks/glm-5p1",
            "name": "GLM 5.1 (SIN)",
            "options": {
                "thinking": {"type": "enabled", "budgetTokens": 32000}
            },
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}}
            },
            "limit": {"context": 202752, "output": 32768}
        },
        "kimi-k2p6": {
            "id": "fireworks/kimi-k2p6",
            "name": "Kimi K2.6 (SIN)",
            "options": {
                "thinking": {"type": "enabled", "budgetTokens": 32000}
            },
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}}
            },
            "limit": {"context": 262144, "output": 32768},
            "modalities": {"input": ["text", "image"], "output": ["text"]}
        },
        "qwen3p6-plus": {
            "id": "accounts/fireworks/models/qwen3p6-plus",
            "name": "Qwen3.6 Plus (SIN)",
            "options": {
                "thinking": {"type": "enabled", "budgetTokens": 32000}
            },
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}}
            },
            "limit": {"context": 131072, "output": 32768},
            "modalities": {"input": ["text", "image"], "output": ["text"]}
        },
        "minimax-m2p7": {
            "id": "fireworks/minimax-m2p7",
            "name": "MiniMax M2.7 (SIN)",
            "options": {
                "thinking": {"type": "enabled", "budgetTokens": 32000}
            },
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}}
            },
            "limit": {"context": 196608, "output": 32768}
        }
    },
    "options": {
        "baseURL": "https://sinatorpool-router.delqhi.com/inference/v1",
        "apiKey": "<DEIN_API_KEY>"
    }
}

cfg.setdefault("provider", {})["fireworks-ai"] = provider

with open(config_path, 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')

print("✅ Reasoning-Configs hinzugefügt!")
print("Prüfe: cat ~/.config/opencode/opencode.json | grep -A 3 '\"thinking\"'")
EOF
```

Verifizieren:
```bash
# Prüfen ob Reasoning-Configs da sind
cat ~/.config/opencode/opencode.json | grep -A 3 '"thinking"'
# Sollte "type": "enabled" anzeigen
```

---
*Last updated: 2026-05-30*

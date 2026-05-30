#!/usr/bin/env bash
# OpenCode Config Repair — Fixes broken opencode.json after failed installer
# Usage: curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash

set -euo pipefail

OPENCODE_DIR="${HOME}/.config/opencode"
CONFIG_FILE="${OPENCODE_DIR}/opencode.json"
BACKUP_DIR="${OPENCODE_DIR}/backups"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

API_KEY="${1:-${FIREWORKS_AI_API_KEY:-<DEIN_API_KEY>}}"

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  OpenCode Config Repair — Emergency Fix${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""

mkdir -p "$OPENCODE_DIR" "$BACKUP_DIR"

if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="${BACKUP_DIR}/opencode-broken-$(date +%Y%m%d-%H%M%S).json"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    log_info "Broken config backed up: ${BACKUP_FILE}"
fi

REPAIR_API_KEY="${API_KEY}" python3 << 'PYEOF'
import json, os

config_path = os.path.expanduser("~/.config/opencode/opencode.json")
api_key = os.environ.get('REPAIR_API_KEY', '<DEIN_API_KEY>')

FIREWORKS_PROVIDER = {
    "npm": "@ai-sdk/fireworks",
    "name": "Fireworks AI",
    "models": {
        "deepseek-v4-pro": {
            "id": "fireworks/deepseek-v4-pro",
            "name": "DeepSeek V4 Pro (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 64000}, "temperature": 0},
            "variants": {
                "off": {"thinking": {"type": "disabled"}, "temperature": 0},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}, "temperature": 0},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}, "temperature": 0},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 64000}, "temperature": 0},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 128000}, "temperature": 0}
            },
            "limit": {"context": 1048576, "output": 65536}
        },
        "glm-5p1": {
            "id": "fireworks/glm-5p1",
            "name": "GLM 5.1 (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
            "variants": {
                "off": {"thinking": {"type": "disabled"}, "temperature": 0},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}, "temperature": 0},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}, "temperature": 0},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}, "temperature": 0}
            },
            "limit": {"context": 202752, "output": 32768}
        },
        "kimi-k2p6": {
            "id": "fireworks/kimi-k2p6",
            "name": "Kimi K2.6 (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
            "variants": {
                "off": {"thinking": {"type": "disabled"}, "temperature": 0},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}, "temperature": 0},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}, "temperature": 0},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}, "temperature": 0}
            },
            "limit": {"context": 262144, "output": 32768},
            "modalities": {"input": ["text", "image"], "output": ["text"]}
        },
        "qwen3p6-plus": {
            "id": "accounts/fireworks/models/qwen3p6-plus",
            "name": "Qwen3.6 Plus (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
            "variants": {
                "off": {"thinking": {"type": "disabled"}, "temperature": 0},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}, "temperature": 0},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}, "temperature": 0},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}, "temperature": 0}
            },
            "limit": {"context": 131072, "output": 32768},
            "modalities": {"input": ["text", "image"], "output": ["text"]}
        },
        "minimax-m2p7": {
            "id": "fireworks/minimax-m2p7",
            "name": "MiniMax M2.7 (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
            "variants": {
                "off": {"thinking": {"type": "disabled"}, "temperature": 0},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}, "temperature": 0},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}, "temperature": 0},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}, "temperature": 0},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}, "temperature": 0}
            },
            "limit": {"context": 196608, "output": 32768}
        }
    },
    "options": {
        "baseURL": "https://sinatorpool-router.delqhi.com/inference/v1",
        "apiKey": api_key
    }
}

can_load = False
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        can_load = True
    except (json.JSONDecodeError, ValueError):
        can_load = False

if can_load:
    print("Existing config is valid JSON — merging Fireworks provider")
    if "$schema" not in cfg:
        cfg["$schema"] = "https://opencode.ai/config.json"
    if "permission" not in cfg:
        cfg["permission"] = "allow"
    if "skills" not in cfg:
        cfg["skills"] = {"paths": [os.path.expanduser("~/.config/opencode/skills")]}
    if "command" not in cfg:
        cfg["command"] = {}
    if "mcp" not in cfg:
        cfg["mcp"] = {}
    cfg.setdefault("provider", {})["fireworks-ai"] = FIREWORKS_PROVIDER
    if "agent" not in cfg:
        cfg["agent"] = {"SIN-Zeus": {"model": "fireworks-ai/deepseek-v4-pro"}}
    if "defaultAgent" not in cfg:
        cfg["defaultAgent"] = "SIN-Zeus"
    if "defaultModel" not in cfg:
        cfg["defaultModel"] = "fireworks-ai/deepseek-v4-pro"
else:
    print("No valid config found — creating fresh config with all 5 models")
    cfg = {
        "$schema": "https://opencode.ai/config.json",
        "permission": "allow",
        "skills": {"paths": [os.path.expanduser("~/.config/opencode/skills")]},
        "command": {},
        "mcp": {},
        "provider": {"fireworks-ai": FIREWORKS_PROVIDER},
        "agent": {"SIN-Zeus": {"model": "fireworks-ai/deepseek-v4-pro"}},
        "defaultModel": "fireworks-ai/deepseek-v4-pro",
        "defaultAgent": "SIN-Zeus"
    }

with open(config_path, 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')

print(f"Config written with {len(cfg['provider']['fireworks-ai']['models'])} models")
PYEOF

log_ok "Config repaired!"

if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    log_ok "JSON is valid"
    HAS_PROVIDER=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print('yes' if 'fireworks-ai' in d.get('provider', {}) else 'no')")
    HAS_REASONING=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); p=d.get('provider',{}).get('fireworks-ai',{}); print('yes' if 'thinking' in str(p) else 'no')")
    MODEL_COUNT=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(len(d.get('provider',{}).get('fireworks-ai',{}).get('models',{})))")
    [ "$HAS_PROVIDER" = "yes" ] && log_ok "Fireworks provider present" || log_warn "Fireworks provider missing"
    [ "$HAS_REASONING" = "yes" ] && log_ok "Reasoning configs present" || log_warn "Reasoning configs missing"
    [ "$MODEL_COUNT" = "5" ] && log_ok "All 5 models present" || log_warn "Expected 5 models, got ${MODEL_COUNT}"
else
    log_error "Config is still broken!"
    exit 1
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Done! OpenCode is ready.${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"

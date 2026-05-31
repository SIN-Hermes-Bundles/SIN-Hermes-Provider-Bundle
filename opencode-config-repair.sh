#!/usr/bin/env bash
# OpenCode Config Repair — Fixes broken opencode.json
# Downloads opencode.json and merges/replaces
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash
#   bash opencode-config-repair.sh [api_key]

set -euo pipefail

OPENCODE_DIR="${HOME}/.config/opencode"
CONFIG_FILE="${OPENCODE_DIR}/opencode.json"
BACKUP_DIR="${OPENCODE_DIR}/backups"
REMOTE_URL="https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCAL_TEMPLATE="${SCRIPT_DIR}/opencode.json"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

API_KEY="${1:-${FIREWORKS_AI_API_KEY:-<DEIN_API_KEY>}}"

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  OpenCode Config Repair${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""

mkdir -p "$OPENCODE_DIR" "$BACKUP_DIR"

if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="${BACKUP_DIR}/opencode-broken-$(date +%Y%m%d-%H%M%S).json"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    log_info "Backup: ${BACKUP_FILE}"
fi

REPAIR_API_KEY="${API_KEY}" REPAIR_LOCAL_FILE="${LOCAL_TEMPLATE}" python3 << 'PYEOF'
import json, os, sys, urllib.request

config_path = os.path.expanduser("~/.config/opencode/opencode.json")
api_key = os.environ.get('REPAIR_API_KEY', '<DEIN_API_KEY>')
remote_url = "https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json"
local_file = os.environ.get('REPAIR_LOCAL_FILE', '')

template = None
if local_file and os.path.exists(local_file):
    with open(local_file) as f:
        template = json.load(f)
    print(f"Loaded template from local file ({len(template.get('provider',{}).get('fireworks-ai',{}).get('models',{}))} models)")
else:
    try:
        with urllib.request.urlopen(remote_url, timeout=15) as resp:
            template = json.loads(resp.read().decode())
        print(f"Downloaded template from GitHub ({len(template.get('provider',{}).get('fireworks-ai',{}).get('models',{}))} models)")
    except Exception as e:
        print(f"ERROR: Failed to download template: {e}", file=sys.stderr)
        sys.exit(1)

template_fw = template.get("provider", {}).get("fireworks-ai", {})
if not template_fw:
    print("ERROR: Template has no fireworks-ai provider", file=sys.stderr)
    sys.exit(1)

template_fw["options"]["apiKey"] = api_key

can_load = False
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        can_load = True
    except (json.JSONDecodeError, ValueError):
        can_load = False

if can_load:
    print("Existing config valid — merging Fireworks provider")
    if "$schema" not in cfg:
        cfg["$schema"] = "https://opencode.ai/config.json"
    cfg.setdefault("provider", {})["fireworks-ai"] = template_fw
else:
    print("Config broken or missing — creating fresh from template")
    cfg = template.copy()
    cfg["provider"]["fireworks-ai"]["options"]["apiKey"] = api_key

with open(config_path, 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')

print(f"Written {len(cfg['provider']['fireworks-ai']['models'])} models")
PYEOF

log_ok "Config repaired!"

if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
    log_ok "JSON valid"
    MODEL_COUNT=$(python3 -c "import json; print(len(json.load(open('$CONFIG_FILE')).get('provider',{}).get('fireworks-ai',{}).get('models',{})))")
    [ "$MODEL_COUNT" = "12" ] && log_ok "All 12 models present" || log_warn "Expected 12 models, got ${MODEL_COUNT}"
else
    log_error "Config still broken!"
    exit 1
fi

echo ""
echo -e "${GREEN}  Done!${NC}"

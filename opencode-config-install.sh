#!/usr/bin/env bash
# OpenCode CLI Fireworks Config Installer
# Downloads opencode.json from repo and merges into existing config
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash
#   curl -fsSL ... | bash -s -- --api-key fw_xxx
#   curl -fsSL ... | bash -s -- --dry-run

set -euo pipefail

OPENCODE_DIR="${HOME}/.config/opencode"
CONFIG_FILE="${OPENCODE_DIR}/opencode.json"
BACKUP_DIR="${OPENCODE_DIR}/backups"
TEMPLATE_URL="https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

API_KEY=""
DRY_RUN=false

while [ $# -gt 0 ]; do
    case "$1" in
        --api-key) API_KEY="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        *) shift ;;
    esac
done

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  OpenCode CLI — Fireworks AI Config Installer${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -z "$API_KEY" ]; then
    if [ -n "${FIREWORKS_AI_API_KEY:-}" ]; then
        API_KEY="$FIREWORKS_AI_API_KEY"
        log_info "Using FIREWORKS_AI_API_KEY from environment"
    else
        echo -n "Enter your Fireworks API Key (fw_... or press Enter for placeholder): "
        read -r API_KEY
        if [ -z "$API_KEY" ]; then
            API_KEY="<DEIN_API_KEY>"
            log_warn "No API key provided — using placeholder"
        fi
    fi
fi

mkdir -p "$OPENCODE_DIR"

if [ -f "$CONFIG_FILE" ]; then
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="${BACKUP_DIR}/opencode-$(date +%Y%m%d-%H%M%S).json"
    if [ "$DRY_RUN" = false ]; then
        cp "$CONFIG_FILE" "$BACKUP_FILE"
    fi
    log_info "Backup: ${BACKUP_FILE}"
fi

if [ "$DRY_RUN" = false ]; then
    INSTALLER_API_KEY="${API_KEY}" python3 << 'PYEOF'
import json, os, urllib.request, sys

config_path = os.path.expanduser("~/.config/opencode/opencode.json")
api_key = os.environ.get('INSTALLER_API_KEY', '<DEIN_API_KEY>')
template_url = "https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json"

# Download template
try:
    with urllib.request.urlopen(template_url, timeout=15) as resp:
        template = json.loads(resp.read().decode())
except Exception as e:
    print(f"ERROR: Failed to download template: {e}", file=sys.stderr)
    sys.exit(1)

template_fw = template.get("provider", {}).get("fireworks-ai", {})
if not template_fw:
    print("ERROR: Template has no fireworks-ai provider", file=sys.stderr)
    sys.exit(1)

template_fw["options"]["apiKey"] = api_key

# Load existing or create new
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            cfg = json.load(f)
    except (json.JSONDecodeError, ValueError):
        cfg = {"$schema": "https://opencode.ai/config.json"}
else:
    cfg = {"$schema": "https://opencode.ai/config.json"}

# Merge provider
cfg.setdefault("provider", {})["fireworks-ai"] = template_fw

# Set defaults only if missing
if "defaultModel" not in cfg:
    cfg["defaultModel"] = "fireworks-ai/deepseek-v4-pro"
if "defaultAgent" not in cfg:
    cfg["defaultAgent"] = "SIN-Zeus"

with open(config_path, 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')

print(f"Configured {len(template_fw['models'])} Fireworks models")
print(f"Base URL: {template_fw['options']['baseURL']}")
PYEOF

    log_ok "opencode.json updated"
else
    log_info "DRY RUN — would download template and merge"
fi

echo ""
echo -e "${GREEN}  Done!${NC}"
echo ""

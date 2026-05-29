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
# 1. Check Pool Router
curl -s http://localhost:9998/health | python3 -m json.tool
# → Expected: {"status": "ok", "pools": [...]}

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
curl -s -X POST http://localhost:9998/inference/v1/chat/completions \
  -H "Content-Type: application/json" \
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

```bash
# Add Fireworks API key
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"

# Verify provider
hermes model

# Test chat
hermes chat -Q -q "say hello"
```

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

---
*Last updated: 2026-05-30*

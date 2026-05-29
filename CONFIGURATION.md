# Configuration Guide

## Overview

The Provider Bundle installs the Pool Router, patches, and configuration for the SINator Fireworks AI pool.

## Main Config

### ~/.hermes/config.yaml

```yaml
# Fireworks Router Config
provider:
  custom:fireworks:
    base_url: http://localhost:9998/inference/v1
    api_key: ${FIREWORKS_AI_API_KEY}

# Pool Router
pool_router:
  port: 9998
  health_check_interval: 30
  
# Proxies
proxies:
  - port: 8888
    key_alias: vortex-viper-336@gmx.de
  - port: 8889
    key_alias: another-alias@gmx.de
  - port: 8890
  - port: 8891
  - port: 8892
  - port: 8893
  - port: 8894
  - port: 8895
  - port: 8896
  - port: 8897
```

## Pool Router Configuration

### Auto-Start Service

```bash
# Check service
launchctl list | grep com.sinator.pool-router

# Service config
~/Library/LaunchAgents/com.sinator.pool-router.plist
```

### Router Settings

```python
# In pool-router.py
MAX_FAILURES = 3
COOLDOWN_SECONDS = 60
HEALTH_CHECK_INTERVAL = 30
```

## Patch Configuration

### 412 Retry Patch

```python
# In error_classifier.py
RETRY_CODES = [412, 413, 429, 500, 502, 503, 504]
MAX_RETRIES = 3
```

### UA-Spoof Patch

```python
# In _ua_patch.py
USER_AGENT = "Mozilla/5.0..."
MAX_RETRIES = 0
```

### V15 Patches

```yaml
# Tool Search config
tool_search:
  mode: auto
  threshold: 0.10
  pinned_tools:
    - tool_search
    - tool_details
    - execute_code
    - todo
    - web_search
    - read_file
    - write_file
    - skills_list
    - skill_view
    - skill_manage
    - browser_navigate
    - browser_snapshot
    - browser_click
    - browser_type
    - browser_scroll
    - browser_console
    - browser_press
    - browser_get_images
    - browser_vision
    - browser_back
```

## Fireworks API Configuration

### Adding API Key

```bash
# Via CLI
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"

# Via config
export FIREWORKS_AI_API_KEY="fw_..."
```

### Model Selection

```bash
# List models
hermes model list

# Set default
hermes model set accounts/fireworks/models/deepseek-v4-flash
```

## Advanced Configuration

### Custom Pool

```bash
# Add proxy
export PROXY_PORT=8898
python3 ~/.hermes/scripts/pool-router.py add-proxy $PROXY_PORT
```

### Health Checks

```bash
# Manual health check
curl http://localhost:9998/health

# Check specific proxy
curl http://localhost:8888/health
```

## Environment Variables

```bash
export FIREWORKS_AI_API_KEY="your-key"
export POOL_ROUTER_PORT=9998
export PROXY_COUNT=10
export LOG_LEVEL=INFO
```

## Troubleshooting

### Router not responding

```bash
# Check logs
tail -f ~/.hermes/logs/pool-router.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.sinator.pool-router.plist
launchctl load ~/Library/LaunchAgents/com.sinator.pool-router.plist
```

### Patches not applied

```bash
# Re-apply
cd ~/.hermes/hermes-agent
git apply patches/error_classifier_412.patch
```

### Config issues

```bash
# Reset
rm ~/.hermes/config.yaml
./install.sh
```

---
*Last updated: 2026-05-30*

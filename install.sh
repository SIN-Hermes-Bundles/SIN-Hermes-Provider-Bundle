#!/usr/bin/env bash
set -euo pipefail
REPO="https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "Installing SIN-Hermes-Provider-Bundle..."
echo ""
echo "This bundle installs:"
echo "  - Pool Router (sinatorpool-router.delqhi.com) with auto-failover across 10 proxies"
echo "  - Auto-start service (runs after reboot, restarts on crash)"
echo "  - Fireworks Config pointing to remote router"
echo "  - 412 PRECONDITION_FAILED retry patch"
echo "  - User-Agent spoof patch"
echo "  - Unlimited max_turns"
echo "  - PR #6318 tool_search backend (7 files: tool_search, registry, model_tools, prompt_builder, system_prompt, agent_init, conversation_loop)"
echo "  - Model Discovery: custom:* provider support (model_tools.py)"
echo ""

# 1. Router Config (sinatorpool-router.delqhi.com)
curl -fsSL "$REPO/config/fireworks-router.yaml" -o "$HERMES_HOME/config.yaml"

# 2. Download pool-router
mkdir -p "$HERMES_HOME/scripts" "$HERMES_HOME/logs"
curl -fsSL "$REPO/scripts/pool-router.py" -o "$HERMES_HOME/scripts/pool-router.py"
chmod +x "$HERMES_HOME/scripts/pool-router.py"

# 3. Install launchd service (auto-start on login, restart on crash)
echo "Installing auto-start service..."
mkdir -p "$LAUNCH_AGENTS"
# Generate plist with absolute paths
python3 -c "
import os
home = os.path.expanduser('~')
plist = f'''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>com.sinator.pool-router</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{home}/.hermes/scripts/pool-router.py</string>
    </array>
    <key>StandardOutPath</key>
    <string>{home}/.hermes/logs/pool-router.log</string>
    <key>StandardErrorPath</key>
    <string>{home}/.hermes/logs/pool-router.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>5</integer>
</dict>
</plist>'''
with open(os.path.expanduser('~/Library/LaunchAgents/com.sinator.pool-router.plist'), 'w') as f:
    f.write(plist)
print('Plist written')
"

# Unload old (beide Namen für Migration) if exists, load new
launchctl unload "$LAUNCH_AGENTS/com.sinhermes.poolrouter.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS/com.sinator.pool-router.plist" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS/com.sinator.pool-router.plist" 2>/dev/null || true

# Wait a moment for router to start
sleep 1
if pgrep -f "pool-router.py" > /dev/null 2>&1; then
    echo "Pool-router auto-start service installed and running."
else
    echo "WARNING: Pool-router not running. Starting manually..."
    nohup python3 "$HERMES_HOME/scripts/pool-router.py" > "$HERMES_HOME/logs/pool-router.log" 2>&1 &
fi

# 4. 412 Patch
if [ -f "$HERMES_HOME/hermes-agent/agent/error_classifier.py" ]; then
  echo "Applying 412 retry patch..."
  curl -fsSL "$REPO/patches/error_classifier_412.patch" -o /tmp/error_classifier_412.patch
  cd "$HERMES_HOME/hermes-agent"
  git apply /tmp/error_classifier_412.patch 2>/dev/null || echo "Patch may already be applied"
fi

# 5. UA-Spoof Patch
echo "Applying User-Agent spoof patch..."
curl -fsSL "$REPO/_ua_patch.py" -o "$HERMES_HOME/hermes-agent/_ua_patch.py"
if ! grep -q "import _ua_patch" "$HERMES_HOME/hermes-agent/run_agent.py" 2>/dev/null; then
  sed -i '' 's/^import os$/import os\nimport _ua_patch  # noqa/' "$HERMES_HOME/hermes-agent/run_agent.py" 2>/dev/null || true
  echo "UA-Spoof patch applied."
fi

# 6. PR #6318 tool_search patches (7 files) + custom:* provider model discovery
echo "Applying PR #6318 tool_search patches..."
curl -fsSL "$REPO/patches/tools/tool_search.py"   -o "$HERMES_HOME/hermes-agent/tools/tool_search.py"
curl -fsSL "$REPO/patches/tools/registry.py"      -o "$HERMES_HOME/hermes-agent/tools/registry.py"
curl -fsSL "$REPO/patches/model_tools.py"          -o "$HERMES_HOME/hermes-agent/model_tools.py"
curl -fsSL "$REPO/patches/agent/prompt_builder.py" -o "$HERMES_HOME/hermes-agent/agent/prompt_builder.py"
curl -fsSL "$REPO/patches/agent/system_prompt.py"  -o "$HERMES_HOME/hermes-agent/agent/system_prompt.py"
curl -fsSL "$REPO/patches/agent/agent_init.py"     -o "$HERMES_HOME/hermes-agent/agent/agent_init.py"
curl -fsSL "$REPO/patches/agent/conversation_loop.py" -o "$HERMES_HOME/hermes-agent/agent/conversation_loop.py"
curl -fsSL "$REPO/patches/hermes_cli/models.py"    -o "$HERMES_HOME/hermes-agent/hermes_cli/models.py"
find "$HERMES_HOME/hermes-agent" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "PR #6318 patches applied (tool_search + model discovery)."

# 8. Set unlimited max_turns
if ! grep -q "max_turns" "$HERMES_HOME/config.yaml"; then
  printf '\nagent:\n  max_turns: 999999\n  max_iterations: 999999\n' >> "$HERMES_HOME/config.yaml"
  echo "Set max_turns=999999 (unlimited)"
fi

# 9. Install own skill into Hermes
mkdir -p "$HERMES_HOME/skills/survey/sin-hermes-provider-setup"
curl -fsSL "$REPO/skills/sin-hermes-provider-setup/SKILL.md" -o "$HERMES_HOME/skills/survey/sin-hermes-provider-setup/SKILL.md"
echo "Provider setup skill installed to Hermes."

echo ""
echo "=========================================="
echo " SIN-Hermes-Provider-Bundle installed!"
echo "=========================================="
echo ""
echo "| Pool Router: sinatorpool-router.delqhi.com → 10 Proxys (8888-8897, auto-failover) |"
echo "| Auto-start:  Enabled (runs on login, restarts on crash)         |"
echo ""
echo "Next step:"
echo "  hermes auth add custom:fireworks --type api-key --api-key \"\$FIREWORKS_AI_API_KEY\""
echo ""
echo "Manage service:"
echo "  launchctl unload ~/Library/LaunchAgents/com.sinator.pool-router.plist  # stop"
echo "  launchctl load ~/Library/LaunchAgents/com.sinator.pool-router.plist    # start"
echo "  pgrep -f pool-router.py                                                  # check"
echo "  tail -f ~/.hermes/logs/pool-router.log                                   # logs"
echo ""
echo "Done!"

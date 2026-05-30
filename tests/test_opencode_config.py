#!/usr/bin/env python3
"""Tests for opencode-config-install.sh and opencode-config-repair.sh.

Runs the ACTUAL shell scripts in isolated temp HOME directories.
Verifies the generated opencode.json matches the reference config exactly.
"""
import json
import os
import subprocess
import sys
import tempfile

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REFERENCE_PROVIDER = {
    "npm": "@ai-sdk/fireworks",
    "name": "Fireworks AI",
    "models": {
        "deepseek-v4-pro": {
            "id": "fireworks/deepseek-v4-pro",
            "name": "DeepSeek V4 Pro (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 128000}},
            },
            "limit": {"context": 1048576, "output": 65536},
        },
        "glm-5p1": {
            "id": "fireworks/glm-5p1",
            "name": "GLM 5.1 (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
            },
            "limit": {"context": 202752, "output": 32768},
        },
        "kimi-k2p6": {
            "id": "fireworks/kimi-k2p6",
            "name": "Kimi K2.6 (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
            },
            "limit": {"context": 262144, "output": 32768},
            "modalities": {"input": ["text", "image"], "output": ["text"]},
        },
        "qwen3p6-plus": {
            "id": "accounts/fireworks/models/qwen3p6-plus",
            "name": "Qwen3.6 Plus (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
            },
            "limit": {"context": 131072, "output": 32768},
            "modalities": {"input": ["text", "image"], "output": ["text"]},
        },
        "minimax-m2p7": {
            "id": "fireworks/minimax-m2p7",
            "name": "MiniMax M2.7 (SIN)",
            "options": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
            "variants": {
                "off": {"thinking": {"type": "disabled"}},
                "low": {"thinking": {"type": "enabled", "budgetTokens": 4000}},
                "medium": {"thinking": {"type": "enabled", "budgetTokens": 16000}},
                "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
                "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}},
            },
            "limit": {"context": 196608, "output": 32768},
        },
    },
    "options": {
        "baseURL": "https://sinatorpool-router.delqhi.com/inference/v1",
    },
}

TEST_API_KEY = "fw_testkey_abc123"


def _run_install(tmpdir, api_key=TEST_API_KEY, existing_config=None):
    config_path = os.path.join(tmpdir, ".config", "opencode", "opencode.json")
    if existing_config is not None:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            if isinstance(existing_config, str):
                f.write(existing_config)
            else:
                json.dump(existing_config, f, indent=2)

    env = os.environ.copy()
    env["HOME"] = tmpdir
    env["FIREWORKS_AI_API_KEY"] = api_key

    script = os.path.join(REPO_DIR, "opencode-config-install.sh")
    result = subprocess.run(
        ["bash", script, "--api-key", api_key],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Install failed (rc={result.returncode}): {result.stderr}\nstdout: {result.stdout}")

    with open(config_path) as f:
        return json.load(f)


def _run_repair(tmpdir, api_key=TEST_API_KEY, existing_config=None, broken=False):
    config_path = os.path.join(tmpdir, ".config", "opencode", "opencode.json")
    if existing_config is not None:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            if broken or isinstance(existing_config, str):
                f.write(existing_config if isinstance(existing_config, str) else json.dumps(existing_config))
            else:
                json.dump(existing_config, f, indent=2)

    env = os.environ.copy()
    env["HOME"] = tmpdir
    env["FIREWORKS_AI_API_KEY"] = api_key

    script = os.path.join(REPO_DIR, "opencode-config-repair.sh")
    result = subprocess.run(
        ["bash", script, api_key],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Repair failed (rc={result.returncode}): {result.stderr}\nstdout: {result.stdout}")

    with open(config_path) as f:
        return json.load(f)


def _assert_valid(cfg, name):
    assert isinstance(cfg, dict), f"[{name}] not dict"
    assert "provider" in cfg, f"[{name}] no provider"
    assert "fireworks-ai" in cfg["provider"], f"[{name}] no fireworks-ai"
    fw = cfg["provider"]["fireworks-ai"]
    assert fw["npm"] == "@ai-sdk/fireworks", f"[{name}] wrong npm"
    assert len(fw["models"]) == 5, f"[{name}] expected 5 models, got {len(fw['models'])}"
    assert fw["options"]["baseURL"] == "https://sinatorpool-router.delqhi.com/inference/v1", f"[{name}] wrong baseURL"


def _assert_provider_matches(provider, name):
    ref = REFERENCE_PROVIDER
    assert provider["npm"] == ref["npm"], f"[{name}] npm"
    assert provider["name"] == ref["name"], f"[{name}] name"
    assert set(provider["models"].keys()) == set(ref["models"].keys()), f"[{name}] model keys: {set(provider['models'].keys())} vs {set(ref['models'].keys())}"
    for m in ref["models"]:
        mr = ref["models"][m]
        mg = provider["models"][m]
        assert mg["id"] == mr["id"], f"[{name}] {m} id"
        assert mg["name"] == mr["name"], f"[{name}] {m} name"
        assert mg["options"] == mr["options"], f"[{name}] {m} options"
        assert set(mg["variants"].keys()) == set(mr["variants"].keys()), f"[{name}] {m} variant keys"
        for v in mr["variants"]:
            assert mg["variants"][v] == mr["variants"][v], f"[{name}] {m} variant {v}"
        assert mg["limit"] == mr["limit"], f"[{name}] {m} limit"
        if "modalities" in mr:
            assert mg.get("modalities") == mr["modalities"], f"[{name}] {m} modalities"
    assert provider["options"]["baseURL"] == ref["options"]["baseURL"], f"[{name}] baseURL"


passed = 0
failed = 0


def _test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        failed += 1


print("=" * 70)
print("  opencode-config — Test Suite (real shell scripts)")
print("=" * 70)
print()

# ── INSTALL ──

print("[Install] Fresh (no existing config)")


def t_install_fresh():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_install(td)
        _assert_valid(cfg, "fresh")
        _assert_provider_matches(cfg["provider"]["fireworks-ai"], "fresh")
        assert cfg["defaultModel"] == "fireworks-ai/deepseek-v4-pro"
        assert cfg["defaultAgent"] == "SIN-Zeus"


_test("fresh", t_install_fresh)

print("[Install] Merge (preserves user settings)")


def t_install_merge():
    with tempfile.TemporaryDirectory() as td:
        existing = {
            "$schema": "https://opencode.ai/config.json",
            "permission": "allow",
            "command": {"my-cmd": {"description": "x", "template": "x"}},
            "mcp": {"my-mcp": {"type": "local", "command": ["x"], "enabled": True}},
            "provider": {"other": {"name": "Other"}},
            "agent": {"my-agent": {"model": "other/m"}},
            "defaultModel": "other/m",
            "defaultAgent": "my-agent",
        }
        cfg = _run_install(td, existing_config=existing)
        _assert_valid(cfg, "merge")
        _assert_provider_matches(cfg["provider"]["fireworks-ai"], "merge")
        assert "other" in cfg["provider"]
        assert "my-cmd" in cfg["command"]
        assert "my-mcp" in cfg["mcp"]
        assert "my-agent" in cfg["agent"]
        assert cfg["defaultModel"] == "other/m"
        assert cfg["defaultAgent"] == "my-agent"


_test("merge", t_install_merge)

print("[Install] Overwrites old fireworks-ai")


def t_install_overwrite():
    with tempfile.TemporaryDirectory() as td:
        existing = {
            "$schema": "https://opencode.ai/config.json",
            "provider": {"fireworks-ai": {"npm": "@ai-sdk/fireworks", "name": "Old", "models": {}, "options": {"baseURL": "http://localhost:9998", "apiKey": "old"}}},
        }
        cfg = _run_install(td, existing_config=existing)
        _assert_valid(cfg, "overwrite")
        assert cfg["provider"]["fireworks-ai"]["options"]["baseURL"] == "https://sinatorpool-router.delqhi.com/inference/v1"


_test("overwrite", t_install_overwrite)

print("[Install] API key")


def t_install_apikey():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_install(td, api_key="fw_REAL_123")
        assert cfg["provider"]["fireworks-ai"]["options"]["apiKey"] == "fw_REAL_123"


_test("apikey", t_install_apikey)

print("[Install] All 5 models × 5 variants")


def t_install_models():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_install(td)
        fw = cfg["provider"]["fireworks-ai"]
        for m in ["deepseek-v4-pro", "glm-5p1", "kimi-k2p6", "qwen3p6-plus", "minimax-m2p7"]:
            assert m in fw["models"], f"missing model {m}"
            for v in ["off", "low", "medium", "high", "max"]:
                assert v in fw["models"][m]["variants"], f"missing variant {v} in {m}"


_test("5models_5variants", t_install_models)

print("[Install] Reasoning budgets")


def t_install_budgets():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_install(td)
        fw = cfg["provider"]["fireworks-ai"]
        assert fw["models"]["deepseek-v4-pro"]["options"]["thinking"]["budgetTokens"] == 64000
        assert fw["models"]["deepseek-v4-pro"]["variants"]["max"]["thinking"]["budgetTokens"] == 128000
        assert fw["models"]["deepseek-v4-pro"]["variants"]["low"]["thinking"]["budgetTokens"] == 4000
        assert fw["models"]["glm-5p1"]["options"]["thinking"]["budgetTokens"] == 32000


_test("budgets", t_install_budgets)

print("[Install] Model IDs")


def t_install_ids():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_install(td)
        fw = cfg["provider"]["fireworks-ai"]
        assert fw["models"]["deepseek-v4-pro"]["id"] == "fireworks/deepseek-v4-pro"
        assert fw["models"]["qwen3p6-plus"]["id"] == "accounts/fireworks/models/qwen3p6-plus"


_test("ids", t_install_ids)

print("[Install] Modalities (vision models)")


def t_install_modalities():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_install(td)
        fw = cfg["provider"]["fireworks-ai"]
        assert fw["models"]["kimi-k2p6"]["modalities"]["input"] == ["text", "image"]
        assert fw["models"]["qwen3p6-plus"]["modalities"]["input"] == ["text", "image"]
        assert "modalities" not in fw["models"]["minimax-m2p7"]


_test("modalities", t_install_modalities)

# ── REPAIR ──

print()
print("[Repair] Broken JSON → fresh config with all 5 models")


def t_repair_broken():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_repair(td, existing_config='{ this is broken json !!!', broken=True)
        _assert_valid(cfg, "repair_broken")
        _assert_provider_matches(cfg["provider"]["fireworks-ai"], "repair_broken")
        assert cfg["defaultModel"] == "fireworks-ai/deepseek-v4-pro"
        assert cfg["defaultAgent"] == "SIN-Zeus"


_test("broken_json", t_repair_broken)

print("[Repair] Valid JSON missing fireworks → merge")


def t_repair_merge():
    with tempfile.TemporaryDirectory() as td:
        existing = {
            "$schema": "https://opencode.ai/config.json",
            "permission": "allow",
            "command": {"my-cmd": {"description": "x", "template": "x"}},
            "mcp": {"my-mcp": {"type": "local", "command": ["x"], "enabled": True}},
            "provider": {"other": {"name": "Other"}},
            "agent": {"my-agent": {"model": "other/m"}},
            "defaultAgent": "my-agent",
            "defaultModel": "other/m",
        }
        cfg = _run_repair(td, existing_config=existing)
        _assert_valid(cfg, "repair_merge")
        _assert_provider_matches(cfg["provider"]["fireworks-ai"], "repair_merge")
        assert "other" in cfg["provider"]
        assert "my-cmd" in cfg["command"]
        assert "my-mcp" in cfg["mcp"]
        assert "my-agent" in cfg["agent"]
        assert cfg["defaultAgent"] == "my-agent"
        assert cfg["defaultModel"] == "other/m"


_test("merge", t_repair_merge)

print("[Repair] Old fireworks → overwrite")


def t_repair_overwrite():
    with tempfile.TemporaryDirectory() as td:
        existing = {
            "$schema": "https://opencode.ai/config.json",
            "provider": {"fireworks-ai": {"npm": "@ai-sdk/fireworks", "name": "Old", "models": {}, "options": {"baseURL": "http://localhost:9998", "apiKey": "old"}}},
        }
        cfg = _run_repair(td, existing_config=existing)
        _assert_valid(cfg, "repair_overwrite")
        assert cfg["provider"]["fireworks-ai"]["options"]["baseURL"] == "https://sinatorpool-router.delqhi.com/inference/v1"
        assert len(cfg["provider"]["fireworks-ai"]["models"]) == 5


_test("overwrite", t_repair_overwrite)

print("[Repair] No config at all → fresh")


def t_repair_noconfig():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_repair(td)
        _assert_valid(cfg, "repair_noconfig")
        _assert_provider_matches(cfg["provider"]["fireworks-ai"], "repair_noconfig")
        assert cfg["defaultModel"] == "fireworks-ai/deepseek-v4-pro"


_test("noconfig", t_repair_noconfig)

print("[Repair] API key")


def t_repair_apikey():
    with tempfile.TemporaryDirectory() as td:
        cfg = _run_repair(td, api_key="fw_REAL_456")
        assert cfg["provider"]["fireworks-ai"]["options"]["apiKey"] == "fw_REAL_456"


_test("apikey", t_repair_apikey)

# ── SHELL / YAML ──

print()
print("[Shell] install.sh syntax")


def t_syntax_install():
    r = subprocess.run(["bash", "-n", os.path.join(REPO_DIR, "opencode-config-install.sh")], capture_output=True, text=True)
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


_test("install_syntax", t_syntax_install)

print("[Shell] repair.sh syntax")


def t_syntax_repair():
    r = subprocess.run(["bash", "-n", os.path.join(REPO_DIR, "opencode-config-repair.sh")], capture_output=True, text=True)
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


_test("repair_syntax", t_syntax_repair)

print("[Shell] Single-quoted heredoc (no $schema expansion)")


def t_heredoc():
    with open(os.path.join(REPO_DIR, "opencode-config-install.sh")) as f:
        c = f.read()
    assert "<< 'PYEOF'" in c
    with open(os.path.join(REPO_DIR, "opencode-config-repair.sh")) as f:
        c = f.read()
    assert "<< 'PYEOF'" in c


_test("heredoc_safe", t_heredoc)

print("[YAML] All configs use remote URL")


def t_yaml():
    for fn in os.listdir(os.path.join(REPO_DIR, "config")):
        if fn.endswith(".yaml"):
            with open(os.path.join(REPO_DIR, "config", fn)) as f:
                c = f.read()
            assert "sinatorpool-router.delqhi.com" in c, f"{fn} missing remote URL"
            assert "localhost:8888" not in c, f"{fn} has localhost:8888"
            assert "localhost:9998" not in c, f"{fn} has localhost:9998"


_test("yaml_remote", t_yaml)

# ── SUMMARY ──

print()
print("=" * 70)
if failed == 0:
    print(f"  ALL {passed} TESTS PASSED")
else:
    print(f"  {passed} PASSED, {failed} FAILED")
print("=" * 70)
sys.exit(1 if failed > 0 else 0)

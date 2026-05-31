#!/usr/bin/env python3
"""Tests for opencode-config-install.sh and opencode-config-repair.sh.

Runs the ACTUAL shell scripts in isolated temp HOME directories.
Verifies the generated opencode.json matches the reference config exactly.
Uses INSTALLER_LOCAL_FILE / REPAIR_LOCAL_FILE env vars so scripts read local
opencode.json template instead of downloading from GitHub (avoids 404 during dev).
"""
import json
import os
import subprocess
import tempfile

import pytest

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(REPO_DIR, "opencode.json")) as _f:
    REFERENCE_PROVIDER = json.load(_f)["provider"]["fireworks-ai"]

MODEL_COUNT = len(REFERENCE_PROVIDER["models"])

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
    env["INSTALLER_LOCAL_FILE"] = os.path.join(REPO_DIR, "opencode.json")

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
    env["REPAIR_LOCAL_FILE"] = os.path.join(REPO_DIR, "opencode.json")

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
    assert len(fw["models"]) == MODEL_COUNT, f"[{name}] expected {MODEL_COUNT} models, got {len(fw['models'])}"
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


# ── INSTALL TESTS ──


class TestInstall:
    def test_fresh(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            _assert_valid(cfg, "fresh")
            _assert_provider_matches(cfg["provider"]["fireworks-ai"], "fresh")

    def test_merge(self):
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

    def test_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            existing = {
                "$schema": "https://opencode.ai/config.json",
                "provider": {"fireworks-ai": {"npm": "@ai-sdk/fireworks", "name": "Old", "models": {}, "options": {"baseURL": "http://localhost:9998", "apiKey": "old"}}},
            }
            cfg = _run_install(td, existing_config=existing)
            _assert_valid(cfg, "overwrite")
            assert cfg["provider"]["fireworks-ai"]["options"]["baseURL"] == "https://sinatorpool-router.delqhi.com/inference/v1"

    def test_apikey(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td, api_key="fw_REAL_123")
            assert cfg["provider"]["fireworks-ai"]["options"]["apiKey"] == "fw_REAL_123"

    def test_all_models_with_variants(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            fw = cfg["provider"]["fireworks-ai"]
            for m_name in REFERENCE_PROVIDER["models"]:
                assert m_name in fw["models"], f"missing model {m_name}"
                for v in ["off", "low", "medium", "high", "max"]:
                    assert v in fw["models"][m_name]["variants"], f"missing variant {v} in {m_name}"

    def test_budgets(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            fw = cfg["provider"]["fireworks-ai"]
            assert fw["models"]["deepseek-v4-pro"]["options"]["thinking"]["budgetTokens"] == 64000
            assert fw["models"]["deepseek-v4-pro"]["variants"]["max"]["thinking"]["budgetTokens"] == 65536
            assert fw["models"]["deepseek-v4-pro"]["variants"]["low"]["thinking"]["budgetTokens"] == 4000

    def test_model_ids(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            fw = cfg["provider"]["fireworks-ai"]
            assert fw["models"]["deepseek-v4-pro"]["id"] == "fireworks/deepseek-v4-pro"
            assert fw["models"]["qwen3p6-plus"]["id"] == "accounts/fireworks/models/qwen3p6-plus"

    def test_modalities(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            fw = cfg["provider"]["fireworks-ai"]
            for m in ["kimi-k2p5", "kimi-k2p6", "kimi-k2p6-turbo", "qwen3p6-plus"]:
                assert fw["models"][m]["modalities"]["input"] == ["text", "image"], f"{m} should be vision"
            assert "modalities" not in fw["models"]["minimax-m2p7"]
            assert "modalities" not in fw["models"]["gpt-oss-120b"]

    def test_temperature_zero(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            fw = cfg["provider"]["fireworks-ai"]
            for m_name, m in fw["models"].items():
                assert m["options"].get("temperature") == 0, f"{m_name} default temp != 0"
                for v_name, v in m["variants"].items():
                    assert v.get("temperature") == 0, f"{m_name}/{v_name} temp != 0"

    def test_output_limits(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_install(td)
            fw = cfg["provider"]["fireworks-ai"]
            for m_name, m in fw["models"].items():
                out = m["limit"]["output"]
                ctx = m["limit"]["context"]
                assert out <= ctx, f"{m_name}: output {out} > context {ctx}"
                budget = m["options"].get("thinking", {}).get("budgetTokens", 0)
                if budget:
                    assert budget <= out, f"{m_name}: default budgetTokens {budget} > output {out}"
                max_b = m.get("variants", {}).get("max", {}).get("thinking", {}).get("budgetTokens", 0)
                if max_b:
                    assert max_b <= out, f"{m_name}: max budgetTokens {max_b} > output {out}"


# ── REPAIR TESTS ──


class TestRepair:
    def test_broken_json(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_repair(td, existing_config='{ this is broken json !!!', broken=True)
            _assert_valid(cfg, "repair_broken")
            _assert_provider_matches(cfg["provider"]["fireworks-ai"], "repair_broken")

    def test_merge(self):
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

    def test_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            existing = {
                "$schema": "https://opencode.ai/config.json",
                "provider": {"fireworks-ai": {"npm": "@ai-sdk/fireworks", "name": "Old", "models": {}, "options": {"baseURL": "http://localhost:9998", "apiKey": "old"}}},
            }
            cfg = _run_repair(td, existing_config=existing)
            _assert_valid(cfg, "repair_overwrite")
            assert cfg["provider"]["fireworks-ai"]["options"]["baseURL"] == "https://sinatorpool-router.delqhi.com/inference/v1"
            assert len(cfg["provider"]["fireworks-ai"]["models"]) == MODEL_COUNT

    def test_noconfig(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_repair(td)
            _assert_valid(cfg, "repair_noconfig")
            _assert_provider_matches(cfg["provider"]["fireworks-ai"], "repair_noconfig")

    def test_apikey(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _run_repair(td, api_key="fw_REAL_456")
            assert cfg["provider"]["fireworks-ai"]["options"]["apiKey"] == "fw_REAL_456"


# ── SHELL / YAML TESTS ──


class TestShell:
    def test_install_syntax(self):
        r = subprocess.run(["bash", "-n", os.path.join(REPO_DIR, "opencode-config-install.sh")], capture_output=True, text=True)
        assert r.returncode == 0, f"Syntax error: {r.stderr}"

    def test_repair_syntax(self):
        r = subprocess.run(["bash", "-n", os.path.join(REPO_DIR, "opencode-config-repair.sh")], capture_output=True, text=True)
        assert r.returncode == 0, f"Syntax error: {r.stderr}"

    def test_heredoc_safe(self):
        with open(os.path.join(REPO_DIR, "opencode-config-install.sh")) as f:
            assert "<< 'PYEOF'" in f.read()
        with open(os.path.join(REPO_DIR, "opencode-config-repair.sh")) as f:
            assert "<< 'PYEOF'" in f.read()

    def test_yaml_remote(self):
        config_dir = os.path.join(REPO_DIR, "config")
        if not os.path.exists(config_dir):
            pytest.skip("no config/ directory")
        for fn in os.listdir(config_dir):
            if fn.endswith(".yaml"):
                with open(os.path.join(config_dir, fn)) as f:
                    c = f.read()
                assert "sinatorpool-router.delqhi.com" in c, f"{fn} missing remote URL"
                assert "localhost:8888" not in c, f"{fn} has localhost:8888"
                assert "localhost:9998" not in c, f"{fn} has localhost:9998"

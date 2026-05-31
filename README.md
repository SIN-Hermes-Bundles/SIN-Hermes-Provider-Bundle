# SIN-Hermes-Provider-Bundle

Hermes Konfiguration für den Fireworks AI Pool — 12 Modelle über zentralen Pool-Router.

**Base URL:** `https://sinatorpool-router.delqhi.com/inference/v1`

---

## Installieren

```bash
mkdir -p ~/.hermes
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/config/fireworks-router.yaml -o ~/.hermes/config.yaml
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"
```

---

## Nutzen

```bash
hermes chat                                              # default: deepseek-v4-pro
hermes chat --model fireworks/glm-5p1                    # GLM 5.1
hermes chat --model fireworks/kimi-k2p6                  # Kimi K2.6 + vision
hermes chat --model fireworks/minimax-m2p7               # MiniMax M2.7
```

### Modelle

| Name | Hermes ID | Thinking | Vision | Context |
|------|-----------|----------|--------|---------|
| DeepSeek V4 Pro | `fireworks/deepseek-v4-pro` | ja | nein | 1M |
| DeepSeek V4 Flash | `fireworks/deepseek-v4-flash` | ja | nein | 1M |
| GLM 5.1 | `fireworks/glm-5p1` | ja | nein | 202K |
| GLM 5.1 Fast | `fireworks/glm-5p1-fast` | ja | nein | 202K |
| Kimi K2.5 | `fireworks/kimi-k2p5` | ja | ja | 262K |
| Kimi K2.6 | `fireworks/kimi-k2p6` | ja | ja | 262K |
| Kimi K2.6 Turbo | `fireworks/kimi-k2p6-turbo` | ja | ja | 262K |
| Qwen3.6 Plus | `fireworks/qwen3p6-plus` | ja | ja | 131K |
| MiniMax M2.5 | `fireworks/minimax-m2p5` | ja | nein | 196K |
| MiniMax M2.7 | `fireworks/minimax-m2p7` | ja | nein | 196K |
| GPT-OSS 120B | `fireworks/gpt-oss-120b` | nein | nein | 131K |
| GPT-OSS 20B | `fireworks/gpt-oss-20b` | nein | nein | 131K |

---

## Was im Repo ist

| Datei | Zweck |
|-------|-------|
| `config/fireworks-router.yaml` | Hermes Config (Single Source of Truth) |
| `INSTALL.md` | Install-Optionen + Troubleshooting |

---

## OpenCode?

Für OpenCode CLI gibt's ein separates Config-Repo:
→ [SIN-Code-FireworksAI-OpenCode-Config](https://github.com/OpenSIN-Code/SIN-Code-FireworksAI-OpenCode-Config)

---

*Stand: 2026-05-31 | Pool: 234 Keys | Pool-Router: sinatorpool-router.delqhi.com*

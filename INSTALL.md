# INSTALL.md — Hermes Fireworks AI Config

---

## Option 1: Copy & Paste (empfohlen)

```bash
mkdir -p ~/.hermes
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/config/fireworks-router.yaml -o ~/.hermes/config.yaml
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"
```

## Option 2: Environment Variable

```bash
export FIREWORKS_AI_API_KEY="fw_DEIN_KEY"
# Config automatisch: ~/.hermes/config.yaml
```

---

## Prerequisites

- macOS oder Linux
- `curl`, `bash`
- Fireworks API Key (`fw_...`)
- Hermes CLI (`pip install hermes`)

---

## Verifikation

```bash
# Config ist gültiges YAML?
python3 -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml')); print('OK')"

# Pool-Router erreichbar?
curl -s https://sinatorpool-router.delqhi.com/inference/v1/models \
  -H "Authorization: Bearer $FIREWORKS_AI_API_KEY"

# Hermes funktioniert?
hermes chat --model fireworks/deepseek-v4-pro -p "hallo"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `hermes auth add` unbekannt | `hermes --help` → Subcommand prüfen |
| `401 Unauthorized` | `FIREWORKS_AI_API_KEY` falsch oder nicht gesetzt |
| `503 Service Unavailable` | Pool-Router down → später nochmal |
| YAML Parse Error | Config neu laden (Option 1) |
| `key_env` funktioniert nicht | API Key direkt in YAML setzen (nicht empfohlen) |

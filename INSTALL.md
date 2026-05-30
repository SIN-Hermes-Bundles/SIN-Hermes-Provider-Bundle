# INSTALL.md — SIN-Hermes-Provider-Bundle

Fireworks AI Pool-Konfiguration für OpenCode CLI. Nichts wird lokal installiert — nur eine Config-Datei heruntergeladen.

---

## Option 1: Copy & Paste (empfohlen)

```bash
mkdir -p ~/.config/opencode
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json -o ~/.config/opencode/opencode.json
```

API-Key eintragen (`fw_DEIN_KEY` durch echten Key ersetzen):

```bash
sed -i '' 's/fw_DEIN_KEY/fw_DEIN_ECHTER_KEY/' ~/.config/opencode/opencode.json
```

Testen:

```bash
opencode chat --provider fireworks-ai --model deepseek-v4-pro
```

## Option 2: One-Liner Installer

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_DEIN_KEY
```

Bestehende Settings bleiben erhalten. Fireworks Provider + 12 Modelle werden hinzugefügt.

## Option 3: Config kaputt? Repair

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash
```

Bewahrt alle bestehenden Settings. Wenn die Datei komplett kaputt ist, erstellt es eine neue mit allen 12 Modellen.

---

## Prerequisites

- macOS oder Linux
- `bash`, `curl`, `python3` (vorinstalliert auf macOS)
- Fireworks API Key (`fw_...`)
- OpenCode CLI (`npm i -g opencode`)

---

## Verifikation

```bash
# Config ist gültiges JSON?
python3 -c "import json; json.load(open('$HOME/.config/opencode/opencode.json'))" && echo "OK"

# 12 Modelle vorhanden?
python3 -c "import json; print(len(json.load(open('$HOME/.config/opencode/opencode.json'))['provider']['fireworks-ai']['models']), 'Modelle')"

# Pool-Router erreichbar?
curl -s https://sinatorpool-router.delqhi.com/inference/v1/models | head -5

# OpenCode funktioniert?
opencode chat --provider fireworks-ai --model deepseek-v4-pro
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `opencode` startet nicht | `opencode.json` kaputt → Option 3 (Repair) |
| `401 Unauthorized` | API-Key falsch → `fw_DEIN_KEY` ersetzen |
| `503 Service Unavailable` | Pool-Router down → später nochmal |
| JSON Parse Error | Repair-Script (Option 3) |
| Weniger als 12 Modelle | Alte Config → Option 1 oder 2 neu ausführen |
| `temperature != 0` | Alte Config → Option 1 neu ausführen |

# INSTALL.md — SIN-Hermes-Provider-Bundle

Fireworks AI Pool-Konfiguration für OpenCode CLI und Hermes. Nichts wird lokal installiert — es wird nur eine Config-Datei heruntergeladen.

---

## Option 1: Copy & Paste (empfohlen)

Lädt die fertige `opencode.json` herunter. Danach nur noch den API-Key eintragen.

```bash
mkdir -p ~/.config/opencode
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode.json -o ~/.config/opencode/opencode.json
```

API-Key eintragen (in der Datei `fw_DEIN_KEY` durch deinen Key ersetzen):

```bash
sed -i '' 's/fw_DEIN_KEY/fw_DEIN_ECHTER_KEY/' ~/.config/opencode/opencode.json
```

Oder manuell: Datei öffnen, `fw_DEIN_KEY` suchen, durch echten Key ersetzen, speichern.

Fertig. Testen:

```bash
opencode chat --provider fireworks-ai --model deepseek-v4-pro
```

## Option 2: One-Liner Installer

Erstellt/aktualisiert `~/.config/opencode/opencode.json`. Bestehende Settings bleiben erhalten.

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-install.sh | bash -s -- --api-key fw_DEIN_KEY
```

## Option 3: Config kaputt? Repair

Wenn `opencode.json` kaputt ist (ungültiges JSON, fehlende Felder, alter Stand):

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/opencode-config-repair.sh | bash
```

Bewahrt alle bestehenden Settings. Fügt Fireworks Provider + 5 Reasoning-Modelle hinzu. Wenn die Datei komplett kaputt ist, erstellt es eine neue.

---

## Hermes

```bash
curl -fsSL https://raw.githubusercontent.com/SIN-Hermes-Bundles/SIN-Hermes-Provider-Bundle/main/config/fireworks-router.yaml -o ~/.hermes/config.yaml
hermes auth add custom:fireworks --type api-key --api-key "$FIREWORKS_AI_API_KEY"
```

---

## Prerequisites

- macOS oder Linux
- `bash`, `curl`, `python3` (vorinstalliert auf macOS)
- Fireworks API Key (`fw_...` — aus dem Pool)
- OpenCode CLI (`npm i -g opencode`)

---

## Verifikation

```bash
# Config ist gültiges JSON?
python3 -c "import json; json.load(open('~/.config/opencode/opencode.json'))" && echo "OK"

# Pool-Router erreichbar?
curl -s https://sinatorpool-router.delqhi.com/inference/v1/models | head -5

# OpenCode funktioniert?
opencode chat --provider fireworks-ai --model deepseek-v4-pro
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `opencode` startet nicht | `opencode.json` ist kaputt → Option 3 (Repair) ausführen |
| `401 Unauthorized` | API-Key falsch → `fw_DEIN_KEY` durch echten Key ersetzen |
| `503 Service Unavailable` | Pool-Router nicht erreichbar → später nochmal versuchen |
| JSON Parse Error | Repair-Script ausführen (Option 3) |
| Model nicht gefunden | `opencode.json` neu laden (Option 1) — alte Version hat weniger Modelle |

# Pool-Wechsel

## Warum wechseln?

Mit dem Pool-Router ist manuelles Wechseln meist nicht nötig — der Router wechselt automatisch bei Fehlern (413, 429, 412, 5xx).

Aber manchmal willst du manuell eingreifen:
- Pool 1 ist langsam (kein Fehler, nur hohe Latenz)
- Du willst testen ob ein bestimmter Pool schneller ist
- Router hat einen Bug und du willst direkt

## Mit Router (empfohlen)

Standard-Config:

```bash
# ~/.hermes/config.yaml:
#   base_url: https://sinatorpool-router.delqhi.com/inference/v1
```

### Zurück zum Router (falls du lokal warst)
```bash
# 1. Config auf Router setzen (EINE Base-URL für alle)
# ~/.hermes/config.yaml:
#   base_url: https://sinatorpool-router.delqhi.com/inference/v1
# 2. Router starten
launchctl load ~/Library/LaunchAgents/com.sinator.pool-router.plist
```

## Ohne Router (direkte Pools — nicht empfohlen)

Lokal am Mac geht auch direkt (ohne Router):

```bash
# base_url: http://localhost:8888/inference/v1   # Pool 1 direkt (nur lokal)
```

Aber Router empfehlenswert — sonst kein Auto-Failover bei 413/429.

## Verifizierung

```bash
# Aktuelle Config
grep "base_url" ~/.hermes/config.yaml

# Router läuft?
pgrep -f pool-router.py

# Sollte zeigen:
#   base_url: https://sinatorpool-router.delqhi.com/inference/v1  (Standard, empfohlen)
```

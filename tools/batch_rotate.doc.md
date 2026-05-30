# batch_rotate.py

Batch Key Generator: Führt `tools/rotate.py` mehrfach hintereinander aus bis ein Ziel-Pool erreicht ist. Hardcoded Credentials (veraltet — bevor Config Manager). Automatische Retry-Logik mit 3-Fehler-Abbruch.

## Berührt

- `tools/rotate.py` — Subprocess für jede Rotation
- `agent_toolbox/api/routes/pool.py` — `/pool/stats` zum Zählen verfügbarer Keys
- `data/fireworksai-pool.json` — Ziel-Datei

## Config / Limits

- **Achtung Hardcoded Credentials:** `delqhi@gmx.de` / `ZOE.jerry2024` / `ZOE.jerry2024!` (vor Config Manager Era)
- **TARGET:** 69 Keys (fix)
- **Max Retries:** 3 konsekutive Fehler → Abbruch + 30s Pause zwischen Fehlern
- **Checkpoint alle 5 Rotationen:** Pool-Stats via API

## Wichtige Entscheidungen

- **Simple Loop:** Keine parallele Ausführung — sequentiell
- **Subprocess Isolierung:** Jede Rotation ist ein eigener Python-Prozess
- **3-Strike-Abbruch:** Bei 3 konsekutiven Fehlern → Stopp (wahrscheinlich Session/Chrome tot)
- **Kein Config Manager:** Credentials sind hardcoded (dieses Script ist aus V11 Era)

## Flow

```
batch_rotate.py starten
  → Pool Stats lesen (verfügbare Keys zählen)
  → Loop:
      → rotate.py als Subprocess starten
      → Output parsen: "ROTATION COMPLETE" + "API Key:"
      → Bei Erfolg: counter++
      → Bei Fehler: failure counter++ → 30s Pause
      → Alle 5 Erfolge: Pool Stats Checkpoint
      → Abbruch wenn: TARGET erreicht ODER 3 konsekutive Fehler
```

## Status

**In Maintenance Mode** — wird nur bei Bedarf verwendet. Aktuelle Rotation via Dashboard Button oder `python tools/rotate.py` direkt.

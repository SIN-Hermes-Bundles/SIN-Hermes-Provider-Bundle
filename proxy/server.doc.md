# server.py

Fireworks Pool Proxy — aiohttp async proxy mit SSE-Streaming für chat/completions. Verteilt Requests über Pool-Router auf 10 Proxy-Instanzen (:8888-:8897).

## Berührt

- `PoolManager` — Key-Lease/Report für Lastverteilung
- `Hermes AI Client` — Empfängt Antworten via `/v1/models` + `/chat/completions`

## Features

- SSE Streaming für chat/completions
- Auto-Failover bei 413/429/412/5xx
- Cooldown nach 3 Fehlern (60s Pause)
- `/v1/models` Handler — liefert alle Fireworks Modelle + Router aus `~/.hermes/models_dev_cache.json`
- `PUBLIC_PROXY_PATHS`: `/v1/models`, `/inference/v1/models`, `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, `/v1/images/generations`

## Config

- Pool-Router: EIN Router (:9998) → 10 Proxys (:8888-:8897)
- Pool-Stats: `available = total - used - suspended`

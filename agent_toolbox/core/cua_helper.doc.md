# cua_helper.py

CUA (Computer Use Agent) Window Detection + Click/Type/State Helpers. Shared zwischen fireworks_service.py und gmx_service.py. Dynamische PID/WID-Erkennung statt Hardcoded-Indizes.

## Berührt

- `fireworks_service.py` — `login_fireworks()` nutzt `find_cua_window()` für AXTextField-Erkennung und `cua_type_text()` für Names
- `gmx_service.py` — historisch für Navigation (jetzt deprecatet → reiner Playwright-Ansatz)

## Config / Limits

- **CUA Driver:** `cua-driver` CLI muss installiert und laufend sein (`cua-driver serve &`)
- **SINATOR_CHROME_PID:** Env-Variable für gezielte PID-Filterung
- **App Name:** "Google Chrome" (case-insensitive)
- **Timeout:** 10s für list_windows, 15s für get_window_state

## Wichtige Entscheidungen

- **CUA NUR FÜR CHROME UI (AXTextField):** `get_window_state()` zeigt Chrome-AX-Tree (Tabs, Bookmarks, Browser-UI), NICHT Web-Content. Checkboxen/Buttons sind darin NICHT sichtbar.
- **CUA type_text NUR für Names:** Funktioniert für AXTextField-Elemente. React Controlled Inputs ignorieren CUA Keyboard-Events → Playwright fill() alternativ
- **CUA NIEMALS für Web-Content:** Terms-Checkbox, Use-Cases, Buttons alle via Playwright
- **Keine Hardcoded PIDs:** `find_cua_window()` ist dynamisch — PID/WID über `cua-driver list_windows`
- **PID Filter optional:** Wenn `SINATOR_CHROME_PID` gesetzt, wird nach PID gefiltert (vermeidet Cross-Chrome-Window-Picks)
- **Fallback:** Minimized/offscreen Windows werden als Second-Pass gescannt

## Flow

```python
# Fenster finden
result = find_cua_window(title_keywords=["fireworks"])
if result:
    pid, wid = result

# AX-Tree scannen
tree = cua_get_window_state(pid, wid)

# Text tippen (NUR AXTextField!)
cua_type_text(pid, "Vorname Nachname")

# Element klicken
cua_click(pid, wid, element_index=42)
```

## Anti-Patterns

| ❌ FALSCH | ✅ RICHTIG |
|-----------|-----------|
| CUA für Checkbox/Button klicken | Playwright `click()` |
| CUA `type_text` für React Inputs | Playwright `fill()` |
| Hardcoded PID (12345) | `find_cua_window()` dynamisch |
| CUA `get_window_state` für Web-Content | Nur für AXTree Chrome UI verwenden |

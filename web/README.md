# Web build (itch.io edition)

SISYPHUS in the browser: the original `sisyphus_game.py` runs inside
[Pyodide](https://pyodide.org) (Python → WebAssembly) with an
[xterm.js](https://xtermjs.org) terminal shell. Everything is bundled
locally — the game makes zero network requests after load, which is
required for itch.io iframe embedding.

## Files

| File | Purpose |
|---|---|
| `index.html` | Entry point; terminal chrome |
| `main.js` | xterm.js ↔ Pyodide bridge, input handling |
| `sisyphus_web.py` | Generated game module (committed so the bundle is reproducible without a Python toolchain on the dev machine) |
| `build.py` | Generates `sisyphus_web.py` from the original `../sisyphus_game.py` via AST transform |
| `xterm/` | xterm.js 5.5 + fit addon, local |
| `pyodide/` | Pyodide core 314.0.4 (runtime + stdlib), local |
| `test_drive.py` / `test_bc.py` | Headless Python bridge tests (simulate the JS side) |
| `test_browser.js` + `commands_*.json` | Real-Chromium E2E playthroughs for all 4 endings |

## Build

```bash
python3 build.py                 # regenerates sisyphus_web.py
python3 test_drive.py            # Ending A + HIDDEN (headless bridge)
python3 test_bc.py               # Ending B + C (headless bridge)

# E2E (needs playwright + a static server on :8766)
python3 -m http.server 8766 &
node test_browser.js commands_a.json "Ending A"
node test_browser.js commands_b.json "Ending B"
node test_browser.js commands_c.json "Ending C"
node test_browser.js commands_hidden.json "Ending HIDDEN"
```

## How the bridge works

`input()` cannot block in a browser. `build.py` therefore rewrites the
three functions that call `input()` (`present_scene`, `choose_final_path`,
`play`) into `async` functions and wraps each `input(...)` call in `await`.
The preamble installs an async `input()` that awaits a JS-resolved future:
the terminal prints `> `, the player types, and Enter resolves the line
into Python. `print()` output is routed through `js.termWrite()` to the
terminal. Game state, scenes, flags, and ending logic are untouched — the
AST transform is purely mechanical.

## Bundle size

`web/` is ~15 MB (Pyodide core dominates). itch.io limits: single file
≤ 200 MB, total ≤ 500 MB, ≤ 1000 files — well within limits.

#!/usr/bin/env python3
"""Drive the generated sisyphus_web.py locally (no browser) to verify the
async bridge works end-to-end. Simulates the JS side: termWrite collects
output, resolveInput feeds commands when Python awaits input()."""
import asyncio
import sys
import types
from pathlib import Path

# --- mock the `js` module exactly like the browser bridge will ---
import sys
import types

_js_mod = types.ModuleType("js")
sys.modules["js"] = _js_mod
OUTPUT = []

def termWrite(s):
    OUTPUT.append(s)


def resolveInput(t):
    raise RuntimeError("resolveInput should be replaced by driver")


def notifyInputStart():
    pass


_js_mod.termWrite = termWrite
_js_mod.resolveInput = resolveInput
_js_mod.notifyInputStart = notifyInputStart

# preamble replaces sys.stdout with the terminal bridge; keep the real one for logging
_real_stdout = sys.stdout

def log(*a):
    _real_stdout.write(" ".join(str(x) for x in a) + "\n")
    _real_stdout.flush()

import js as _js_mod  # noqa: E402  (resolves to the mocked module)
WEB = Path("/tmp/sisyphus-web/sisyphus_web.py")
import sisyphus_web as web  # noqa: E402


def run_with(commands, label):
    """Feed commands in order, run play(), return collected output text."""
    global OUTPUT
    OUTPUT = []
    cmds = list(commands)

    async def feed():
        for c in cmds:
            for _ in range(2000):
                if web._pending_input is not None:
                    break
                await asyncio.sleep(0.001)
            if web._pending_input is None:
                raise RuntimeError("game finished before all commands consumed")
            web.resolveInput(c)
            await asyncio.sleep(0.005)

    async def main():
        game = asyncio.ensure_future(web.play())
        await asyncio.sleep(0.05)  # let INTRO print
        feeder = asyncio.ensure_future(feed())
        await game
        feeder.cancel()
        try:
            await feeder
        except asyncio.CancelledError:
            pass

    asyncio.run(main())
    text = "".join(OUTPUT)
    # find ending line
    for line in reversed(text.splitlines()):
        if line.strip().startswith("Ending "):
            return text, line.strip()
    return text, "NO ENDING FOUND"


SCENES = [
    ["LOOK LOBBY", "LOOK DESK", "ASK CARLA", "READ DISPATCH", "CONTINUE"],
    ["LOOK OFFICE", "ASK BELL", "READ CASEBOARD", "CONTINUE"],
    ["LOOK PORCH", "LOOK DRIVE", "ASK PATROLMAN", "CONTINUE"],
    ["LOOK FOYER", "LOOK DESK", "READ CALENDAR", "READ DRAWER", "CONTINUE"],
    ["LOOK PANTRY", "LOOK ROOM", "READ NOTEBOOK", "CONTINUE"],
    ["LOOK KITCHEN", "LOOK SINK", "LOOK PORCH", "CONTINUE"],
    ["ASK EVELYN", "READ BIBLE", "CONTINUE"],
    ["LOOK ROOM", "LOOK RADIO", "CONTINUE"],
    ["ASK NORMA", "READ FILE", "CONTINUE"],
    ["READ MEMO", "READ REPORTS", "CONTINUE"],
    ["CALL ROURKE", "HOLD FILES", "CONTINUE"],  # 4.3 both options
    ["LOOK BAR", "ASK BELL", "DRINK WHISKEY", "CONTINUE"],
    ["READ ENVELOPE", "ASK BELL", "CONTINUE"],
    ["CALL MARA", "DRINK WHISKEY", "CONTINUE"],  # 5.3 both options
    ["LOOK HOLLOW", "LOOK RADIO", "CONTINUE"],
    ["ASK GABRIEL", "CONTINUE"],
    ["READ COPY", "CONTINUE"],
    ["LOOK TABLE", "ASK EVELYN", "CONTINUE"],
    ["READ PHOTO", "LOOK PORCH", "CONTINUE"],
]


def full_path(final=None):
    cmds = [c for s in SCENES for c in s]
    if final:
        cmds += [final]
    return cmds


if __name__ == "__main__":
    # Path 1: everything + CALL ROURKE + CALL MARA -> expect Ending A
    text, ending = run_with(full_path(), "path1")
    log(f"PATH1: {ending}")
    ok1 = ending == "Ending A"
    if not ok1:
        log("--- tail ---")
        for line in text.splitlines()[-40:]:
            log(line)

    # Path 2: minimal + low courage path -> expect Ending C (or B)
    text2, ending2 = run_with(
        ["ASK CARLA", "CONTINUE",
         "ASK BELL", "CONTINUE",
         "LOOK PORCH", "CONTINUE",
         "LOOK DESK", "CONTINUE",
         "READ NOTEBOOK", "CONTINUE",
         "LOOK KITCHEN", "CONTINUE",
         "ASK EVELYN", "CONTINUE",
         "LOOK ROOM", "CONTINUE",
         "READ FILE", "CONTINUE",
         "READ MEMO", "CONTINUE",
         "HOLD FILES", "CONTINUE",
         "ASK BELL", "CONTINUE",
         "READ ENVELOPE", "CONTINUE",
         "DRINK WHISKEY", "CONTINUE",
         "LOOK RADIO", "CONTINUE",
         "ASK GABRIEL", "CONTINUE",
         "READ COPY", "CONTINUE",
         "ASK EVELYN", "CONTINUE",
         "READ PHOTO", "CONTINUE",
         "KILL"], "path2")
    log(f"PATH2: {ending2}")

    # Path 3: HIDDEN ending attempt — heavy whiskey + low lucidity
    text3, ending3 = run_with(
        ["ASK CARLA", "CONTINUE",
         "ASK BELL", "CONTINUE",
         "LOOK PORCH", "CONTINUE",
         "LOOK DESK", "CONTINUE",
         "READ NOTEBOOK", "CONTINUE",
         "LOOK KITCHEN", "CONTINUE",
         "ASK EVELYN", "CONTINUE",
         "LOOK ROOM", "CONTINUE",
         "READ FILE", "CONTINUE",
         "READ MEMO", "CONTINUE",
         "CALL ROURKE", "CONTINUE",
         "ASK BELL", "DRINK WHISKEY", "DRINK WHISKEY", "DRINK WHISKEY", "CONTINUE",
         "READ ENVELOPE", "CONTINUE",
         "DRINK WHISKEY", "DRINK WHISKEY", "DRINK WHISKEY", "DRINK WHISKEY", "CONTINUE",
         "LOOK RADIO", "CONTINUE",
         "ASK GABRIEL", "CONTINUE",
         "READ COPY", "CONTINUE",
         "ASK EVELYN", "CONTINUE",
         "READ PHOTO", "LOOK PORCH", "CONTINUE",
         "TURN"], "path3")
    log(f"PATH3: {ending3}")

    log(f"RESULT: {'ALL OK' if ok1 else 'FAIL'}")

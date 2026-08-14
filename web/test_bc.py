#!/usr/bin/env python3
"""Verify Ending B and Ending C deterministically through the web bridge."""
import asyncio
import sys
import types
from pathlib import Path

_js_mod = types.ModuleType("js")
sys.modules["js"] = _js_mod
OUTPUT = []


def termWrite(s):
    OUTPUT.append(s)


def resolveInput(t):
    raise RuntimeError("should be replaced by driver")


def notifyInputStart():
    pass


_js_mod.termWrite = termWrite
_js_mod.resolveInput = resolveInput
_js_mod.notifyInputStart = notifyInputStart

_real_stdout = sys.stdout


def log(*a):
    _real_stdout.write(" ".join(str(x) for x in a) + "\n")
    _real_stdout.flush()


import sisyphus_web as web  # noqa: E402


def run_with(commands):
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
        await asyncio.sleep(0.05)
        feeder = asyncio.ensure_future(feed())
        await game
        feeder.cancel()
        try:
            await feeder
        except asyncio.CancelledError:
            pass

    asyncio.run(main())
    text = "".join(OUTPUT)
    for line in reversed(text.splitlines()):
        if line.strip().startswith("Ending "):
            return line.strip()
    return "NO ENDING"


# Ending B: high courage, NO outside contact (avoid A), final choice BURN
# ASK CARLA(+1c) NOTEBOOK(+1c+1r) FILE(+2c+1l) PORCH(+1c) ENVELOPE(+1c+1r)
# PHOTO(+1c) ROURKE(+1c sent_evidence) — no MARA -> not A
pathB = [
    "ASK CARLA", "CONTINUE",          # c4
    "ASK BELL", "CONTINUE",
    "LOOK PORCH", "CONTINUE",         # c5
    "LOOK DESK", "CONTINUE",
    "READ NOTEBOOK", "CONTINUE",      # c6 r5
    "LOOK KITCHEN", "CONTINUE",
    "ASK EVELYN", "CONTINUE",
    "LOOK ROOM", "CONTINUE",
    "READ FILE", "CONTINUE",          # c8(cap) l5
    "READ MEMO", "CONTINUE",
    "CALL ROURKE", "CONTINUE",        # sent_evidence, c8
    "ASK BELL", "CONTINUE",
    "READ ENVELOPE", "CONTINUE",      # c8 r6
    "CONTINUE",                       # 5.3: no call -> outside_contact stays False
    "LOOK RADIO", "CONTINUE",
    "ASK GABRIEL", "CONTINUE",
    "READ COPY", "CONTINUE",          # c8 l4 r5 omen1
    "ASK EVELYN", "CONTINUE",
    "READ PHOTO", "CONTINUE",         # c8
    "BURN",                           # final choice
]

# Ending C: keep courage < 6 -> no final choice -> C by default
pathC = [
    "ASK CARLA", "CONTINUE",          # c4
    "ASK BELL", "CONTINUE",
    "LOOK PORCH", "CONTINUE",         # c5  (porch gives +1)
    "LOOK DESK", "CONTINUE",
    "READ NOTEBOOK", "CONTINUE",      # c6!! careful -> would allow final choice
    "LOOK KITCHEN", "CONTINUE",
    "ASK EVELYN", "CONTINUE",
    "LOOK ROOM", "CONTINUE",
    "READ FILE", "CONTINUE",          # c8
    "READ MEMO", "CONTINUE",
    "HOLD FILES", "CONTINUE",
    "ASK BELL", "CONTINUE",
    "READ ENVELOPE", "CONTINUE",      # c8
    "CONTINUE",
    "LOOK RADIO", "CONTINUE",
    "ASK GABRIEL", "CONTINUE",
    "READ COPY", "CONTINUE",
    "ASK EVELYN", "CONTINUE",
    "READ PHOTO", "CONTINUE",
    "KILL",                           # if final choice appears -> C; else default C
]

if __name__ == "__main__":
    eB = run_with(pathB)
    log(f"Ending B path -> {eB}")
    eC = run_with(pathC)
    log(f"Ending C path -> {eC}")
    ok = eB == "Ending B" and eC == "Ending C"
    log(f"BC RESULT: {'OK' if ok else 'FAIL'}")

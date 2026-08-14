/* SISYPHUS — itch.io web build.
 * Terminal shell: xterm.js. Python runtime: Pyodide (local, no CDN).
 * The game itself (sisyphus_game.py) is executed unmodified in logic;
 * build.py only rewrites input()/print() plumbing to async JS bridges.
 */
(function () {
  "use strict";

  const term = new Terminal({
    cursorBlink: true,
    fontSize: 15,
    fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace',
    lineHeight: 1.35,
    scrollback: 2000,
    theme: {
      background: "#0a0e0a",
      foreground: "#c8d6c2",
      cursor: "#d8e8d0",
      selectionBackground: "#2a3628",
    },
  });
  const fit = new FitAddon.FitAddon();
  term.loadAddon(fit);

  const termWrap = document.getElementById("terminal");
  term.open(termWrap);
  fit.fit();
  window.addEventListener("resize", () => fit.fit());

  // Make sure the terminal captures keyboard input immediately.
  term.focus();
  termWrap.addEventListener("pointerdown", () => term.focus());
  document.addEventListener("keydown", (e) => {
    if (document.activeElement !== term.textarea) term.focus();
  });

  // ---------------------------------------------------------------
  // Input handling: line-buffered, echoed locally, delivered to Python
  // only while Python is waiting for input.
  // ---------------------------------------------------------------
  let inputBuffer = "";
  let waitingForInput = false;
  let gameOver = false;

  function promptActive() {
    return waitingForInput && !gameOver;
  }

  term.onData((data) => {
    if (gameOver) return;
    if (data === "\r" || data === "\n") {
      if (!promptActive()) {
        // stray Enter: just echo a newline
        term.write("\r\n");
        return;
      }
      term.write("\r\n");
      const line = inputBuffer;
      inputBuffer = "";
      waitingForInput = false;
      window.resolveInput(line);
      return;
    }
    if (data === "\x7f" || data === "\b") {
      if (inputBuffer.length > 0) {
        inputBuffer = inputBuffer.slice(0, -1);
        term.write("\b \b");
      }
      return;
    }
    if (data === "\x03") {
      // Ctrl-C: clear the current line (do not kill Python)
      while (inputBuffer.length > 0) {
        inputBuffer = inputBuffer.slice(0, -1);
        term.write("\b \b");
      }
      term.write("^C\r\n");
      if (promptActive()) {
        term.write("> ");
      }
      return;
    }
    // Ignore other control sequences (arrows, etc.)
    if (data.length === 1 && data.charCodeAt(0) >= 0x20) {
      inputBuffer += data;
      term.write(data);
    }
  });

  // ---------------------------------------------------------------
  // Python <-> JS bridges
  // ---------------------------------------------------------------
  window.termWrite = function (s) {
    // Python print() output; normalize LF -> CRLF for the terminal
    term.write(String(s).replace(/\n/g, "\r\n"));
  };

  window.notifyInputStart = function () {
    waitingForInput = true;
  };

  // Test/automation hook: true while Python awaits a command line
  window.__gameWaiting = function () {
    return waitingForInput && !gameOver;
  };
  window.__gameOver = function () {
    return gameOver;
  };
  window.__termRows = function () {
    // Full terminal history (incl. scrollback), not just the visible DOM rows.
    const buf = term.buffer.active;
    const lines = [];
    for (let i = 0; i < buf.length; i++) {
      lines.push(buf.getLine(i).translateToString(true));
    }
    return lines;
  };

  window.resolveInput = function (text) {
    // Resolved by the Python side synchronously via globals; this
    // function is also the target of the bridge above.
    if (window.__pyodide) {
      window.__pyodide.globals.get("resolveInput")(text);
    }
  };

  // ---------------------------------------------------------------
  // Boot Pyodide from local files, then run the game.
  //
  // indexURL must be an absolute URL derived from this script's own
  // location: relative paths break when the game is embedded in an
  // iframe (itch.io) or served from a sub-path. All Pyodide files
  // (pyodide.asm.wasm, python_stdlib.zip, pyodide-lock.json) are
  // resolved against it.
  // ---------------------------------------------------------------
  const loading = document.getElementById("loading");

  function pyodideBase() {
    const scriptSrc = document.currentScript && document.currentScript.src;
    if (scriptSrc) {
      return scriptSrc.slice(0, scriptSrc.lastIndexOf("/") + 1) + "pyodide/";
    }
    // Fallback: page location
    return new URL("pyodide/", document.baseURI).href;
  }

  async function boot() {
    try {
      const base = pyodideBase();
      const pyodide = await loadPyodide({
        indexURL: base,
        // Some static hosts (itch.io) block .zip files, which would make
        // Pyodide fail with "Failed to import encodings". The stdlib is
        // shipped under a neutral .data extension and pointed to explicitly.
        stdLibURL: base + "python_stdlib.data",
        stdout: (s) => window.termWrite(s),
        stderr: (s) => window.termWrite(s),
      });
      window.__pyodide = pyodide;

      const resp = await fetch("sisyphus_web.py");
      if (!resp.ok) throw new Error("sisyphus_web.py missing: HTTP " + resp.status);
      const code = await resp.text();

      loading.classList.add("hidden");

      // Run the whole game (async play() driven by our bridges).
      await pyodide.runPythonAsync(code + "\nawait play()\n");
      gameOver = true;
    } catch (err) {
      loading.classList.add("hidden");
      gameOver = true;
      if (err && err.constructor && err.constructor.name === "PythonError") {
        term.write("\r\n[python] " + String(err.message).replace(/\n/g, "\r\n") + "\r\n");
      } else if (err && String(err.message).includes("SystemExit")) {
        term.write("\r\n[game exited]\r\n");
      } else {
        term.write("\r\n[fatal] " + String(err && err.message ? err.message : err).replace(/\n/g, "\r\n") + "\r\n");
      }
    }
  }

  boot();
})();

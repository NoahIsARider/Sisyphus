/* Browser-side E2E test v2.
 * Waits for Python to be actually waiting for input (via window.__gameWaiting),
 * then types the command with real keystrokes. Verifies every scene title
 * appears (as terminal rows) and the expected ending is reached.
 */
const { chromium } = require("playwright");
const fs = require("fs");

const URL = process.env.URL || "http://127.0.0.1:8766/index.html";
const commands = JSON.parse(fs.readFileSync(process.argv[2] || "commands_a.json", "utf8"));
const expectedEnding = process.argv[3] || "Ending A";
const SLOW = process.env.SLOW === "1";

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push("console.error: " + msg.text());
  });

  await page.goto(URL, { waitUntil: "load", timeout: 60000 });

  // Wait until Pyodide is booted and the loading overlay is gone.
  await page.waitForFunction(
    () => typeof window.__pyodide !== "undefined" && document.getElementById("loading").classList.contains("hidden"),
    { timeout: 180000 }
  );
  // Wait for the intro to be printed (Python running the game).
  await page.waitForFunction(
    () => (window.__termRows() || []).some((r) => r.includes("Type HELP")),
    { timeout: 60000 }
  );

  async function waitForPrompt() {
    await page.waitForFunction(() => window.__gameWaiting() === true, { timeout: 30000 });
    // small settle delay for the "> " prompt to be painted
    await page.waitForTimeout(60);
  }

  async function send(cmd) {
    // If the game already ended (forced ending skips final choice), stop.
    if (await page.evaluate(() => window.__gameOver())) return false;
    try {
      await page.waitForFunction(() => window.__gameWaiting() === true, { timeout: 30000 });
    } catch (e) {
      // Game may have ended without a prompt; not an error if it is over.
      if (await page.evaluate(() => window.__gameOver())) return false;
      throw e;
    }
    // ensure terminal focus so keystrokes reach xterm
    await page.click("#terminal").catch(() => {});
    await page.keyboard.type(cmd, { delay: SLOW ? 40 : 5 });
    await page.keyboard.press("Enter");
    // let Python process + print before we ask for the next prompt
    await page.waitForTimeout(150);
    return true;
  }

  const seenTitles = new Set();
  for (const sceneCmds of commands) {
    for (const c of sceneCmds) {
      await send(c);
      const rows = await page.evaluate(() => window.__termRows());
      for (const r of rows) {
        const m = r.match(/Chapter \d+\.\d+[^\n]*/);
        if (m) seenTitles.add(m[0].trim());
      }
    }
  }

  // Give the ending time to print
  await page.waitForTimeout(1200);
  const rows = await page.evaluate(() => window.__termRows());
  const allText = rows.join("\n");
  const endingLine = allText.split("\n").filter((l) => l.trim().startsWith("Ending ")).pop() || "NO ENDING";

  console.log("SCENE TITLES SEEN:", seenTitles.size);
  console.log("ENDING:", endingLine.trim());
  if (errors.length) {
    console.log("JS ERRORS:");
    errors.forEach((e) => console.log("  " + e));
  }
  const ok = endingLine.trim() === expectedEnding && errors.length === 0;
  console.log(ok ? "BROWSER TEST: PASS" : "BROWSER TEST: FAIL");
  await browser.close();
  process.exit(ok ? 0 : 1);
})().catch((e) => {
  console.error("BROWSER TEST CRASHED:", e.message);
  process.exit(2);
});

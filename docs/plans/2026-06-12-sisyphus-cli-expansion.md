# Sisyphus CLI Expansion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand `SISYPHUS` into a denser literary command-line game with pseudo-freeform verbs such as `LOOK`, `ASK`, `READ`, `CALL`, and `DRINK`, while deepening chapter prose and long-form dialogue.

**Architecture:** Replace the current one-prompt-per-scene structure with a reusable scene engine that supports repeated commands, scene objects, scene topics, and gated exits. Keep branching shallow: commands should mostly alter tone, reveal layered text, and adjust hidden state rather than fork the plot. Preserve the current ending logic while making earlier scenes feel more exploratory and novelistic.

**Tech Stack:** Python 3 standard library, `unittest`, markdown script bible in `sisyphus_cli_script.md`

---

### Task 1: Add failing tests for command parsing and scene interactions

**Files:**
- Modify: `d:\Projects\其他项目\创作空间\Sisyphus\tests\test_sisyphus_game.py`
- Test: `d:\Projects\其他项目\创作空间\Sisyphus\tests\test_sisyphus_game.py`

**Step 1: Write the failing tests**

```python
def test_parse_command_splits_verb_and_target(self):
    verb, target = parse_command("LOOK DESK")
    self.assertEqual((verb, target), ("LOOK", "DESK"))

def test_scene_handles_known_object_lookup(self):
    scene = build_scene(...)
    output = run_scene_command(scene, state, "LOOK DESK")
    self.assertIn("desk", output.lower())

def test_continue_requires_scene_completion_flag(self):
    scene = build_scene(...)
    result = run_scene_command(scene, state, "CONTINUE")
    self.assertIn("not done", result.lower())
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s 'd:\Projects\其他项目\创作空间\Sisyphus\tests' -v`
Expected: FAIL with missing parser / scene command helpers.

**Step 3: Write minimal implementation**

Create parser helpers and scene command helpers in `sisyphus_game.py`, then expose small testable functions for scene command resolution.

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s 'd:\Projects\其他项目\创作空间\Sisyphus\tests' -v`
Expected: PASS for parser and scene interaction tests.

**Step 5: Commit**

```bash
git add tests/test_sisyphus_game.py sisyphus_game.py
git commit -m "test: add scene command coverage"
```

### Task 2: Refactor the CLI engine around pseudo-freeform scene commands

**Files:**
- Modify: `d:\Projects\其他项目\创作空间\Sisyphus\sisyphus_game.py`
- Test: `d:\Projects\其他项目\创作空间\Sisyphus\tests\test_sisyphus_game.py`

**Step 1: Write the failing test**

```python
def test_scene_command_can_unlock_progress_after_key_topics(self):
    scene = build_scene(...)
    run_scene_command(scene, state, "ASK GABRIEL")
    run_scene_command(scene, state, "READ FILE")
    result = run_scene_command(scene, state, "CONTINUE")
    self.assertIn("advance", result.lower())
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s 'd:\Projects\其他项目\创作空间\Sisyphus\tests' -v`
Expected: FAIL because scene completion gating does not exist yet.

**Step 3: Write minimal implementation**

Implement:
- `parse_command()`
- `run_scene_command()`
- scene data with `look_texts`, `ask_texts`, `read_texts`, `call_texts`
- one-shot or repeatable interactions
- scene completion requirement list
- shared help / status / think / continue behavior

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s 'd:\Projects\其他项目\创作空间\Sisyphus\tests' -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add sisyphus_game.py tests/test_sisyphus_game.py
git commit -m "feat: add pseudo-freeform scene commands"
```

### Task 3: Deepen chapter prose and long conversations in the script bible

**Files:**
- Modify: `d:\Projects\其他项目\创作空间\Sisyphus\sisyphus_cli_script.md`

**Step 1: Write the failing test**

Manual acceptance criteria:
- each main chapter gains at least one substantial prose or dialogue expansion
- more environmental `LOOK` material is available
- more `ASK`/`CALL`/`READ` text banks exist for runtime reuse

**Step 2: Run acceptance check to verify it is not yet complete**

Read the chapter sections and note missing command-specific text banks for several rooms and characters.

**Step 3: Write minimal implementation**

Add:
- chapter-specific command banks
- longer Bell / Evelyn / Gabriel exchanges
- more object descriptions for Wren house, police station, hospital, archive, and bar
- more recurring images tied to porches, jars, rust, fluorescent light, and paper

**Step 4: Run acceptance check to verify it passes**

Re-read the updated sections and confirm the command system can draw on them.

**Step 5: Commit**

```bash
git add sisyphus_cli_script.md
git commit -m "feat: expand literary scene banks"
```

### Task 4: Verify the playable flow end-to-end

**Files:**
- Modify: `d:\Projects\其他项目\创作空间\Sisyphus\sisyphus_game.py`
- Test: `d:\Projects\其他项目\创作空间\Sisyphus\tests\test_sisyphus_game.py`

**Step 1: Write the failing test**

```python
def test_endings_still_resolve_after_scene_engine_refactor(self):
    state = GameState(...)
    self.assertEqual(determine_ending(state), "A")
```

**Step 2: Run test to verify it fails if refactor broke behavior**

Run: `python -m unittest discover -s 'd:\Projects\其他项目\创作空间\Sisyphus\tests' -v`

**Step 3: Write minimal implementation**

Fix any regressions and update the main loop so scenes remain finishable with scripted input.

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s 'd:\Projects\其他项目\创作空间\Sisyphus\tests' -v`
Expected: PASS.

Then run:

`@('LOOK DESK','ASK CARLA','THINK','CONTINUE',...) | python 'd:\Projects\其他项目\创作空间\Sisyphus\sisyphus_game.py'`

Expected: game accepts pseudo-freeform commands and reaches an ending.

**Step 5: Commit**

```bash
git add sisyphus_game.py tests/test_sisyphus_game.py
git commit -m "test: verify expanded cli flow"
```

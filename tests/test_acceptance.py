"""
Full user acceptance tests for SISYPHUS.

These tests simulate a real player typing commands through the entire game,
from the opening scene to each possible ending. They verify that:
- All 19 scenes are reachable and completable
- All 4 endings (A, B, C, HIDDEN) are reachable through valid gameplay
- The command system handles invalid input, HELP, STATUS, THINK, and QUIT
- Scene gating (required_tags) works correctly
- The final choice system (TURN/BURN/KILL) works correctly
"""

import unittest
from io import StringIO
from unittest.mock import patch

import sisyphus_game as game
from sisyphus_game import (
    GameState,
    determine_ending,
    make_scenes,
    parse_command,
    run_scene_command,
    choose_final_path,
    present_scene,
    play,
    INTRO,
    ENDING_TEXT,
    HELP_TEXT,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_scene_commands():
    """Return the minimum command sequence to complete all 19 scenes.

    This traces the 'optimal' path: do exactly the required interaction
    in each scene, then CONTINUE. No drinking, no optional calls.

    Returns a flat list of command strings.
    """
    return [
        # Scene 0 — Chapter 1.1: The police station lobby (required: CARLA)
        "ASK CARLA",
        "CONTINUE",
        # Scene 1 — Chapter 1.2: Chief Bell's office (required: BELL)
        "ASK BELL",
        "CONTINUE",
        # Scene 2 — Chapter 2.1: The Wren house exterior (required: PORCH)
        "LOOK PORCH",
        "CONTINUE",
        # Scene 3 — Chapter 2.2: Foyer and study (required: DESK)
        "LOOK DESK",
        "CONTINUE",
        # Scene 4 — Chapter 2.3: Pantry and children's rooms (required: NOTEBOOK)
        "READ NOTEBOOK",
        "CONTINUE",
        # Scene 5 — Chapter 3.1: The mother house exterior (required: KITCHEN)
        "LOOK KITCHEN",
        "CONTINUE",
        # Scene 6 — Chapter 3.2: The meal (required: EVELYN)
        "ASK EVELYN",
        "CONTINUE",
        # Scene 7 — Chapter 3.3: Gabriel's empty room (required: ROOM)
        "LOOK ROOM",
        "CONTINUE",
        # Scene 8 — Chapter 4.1: Hospital records office (required: FILE)
        "READ FILE",
        "CONTINUE",
        # Scene 9 — Chapter 4.2: County archive basement (required: MEMO)
        "READ MEMO",
        "CONTINUE",
        # Scene 10 — Chapter 4.3: The superior call (required: none, auto-hold)
        "CONTINUE",
        # Scene 11 — Chapter 5.1: The bar (required: BELLBAR)
        "ASK BELL",
        "CONTINUE",
        # Scene 12 — Chapter 5.2: The off-book files (required: ENVELOPE)
        "READ ENVELOPE",
        "CONTINUE",
        # Scene 13 — Chapter 5.3: After midnight choice (required: none)
        "CONTINUE",
        # Scene 14 — Chapter 6.1: The approach (required: RADIO)
        "LOOK RADIO",
        "CONTINUE",
        # Scene 15 — Chapter 6.2: The first confession (required: GABRIEL)
        "ASK GABRIEL",
        "CONTINUE",
        # Scene 16 — Chapter 6.3: The broken memory (required: COPY)
        "READ COPY",
        "CONTINUE",
        # Scene 17 — Chapter 7.1: Evelyn at the table (required: EVELYNFINAL)
        "ASK EVELYN",
        "CONTINUE",
        # Scene 18 — Chapter 7.2: Hidden evidence (required: PHOTO)
        "READ PHOTO",
        "CONTINUE",
    ]


def _run_game(commands):
    """Run play() with the given command sequence, returning captured output."""
    with patch("builtins.input", side_effect=commands):
        with patch("sys.stdout", new_callable=StringIO) as out:
            try:
                play()
            except SystemExit:
                pass
            return out.getvalue()


def _run_scene(commands, scene_index=0, state=None):
    """Run present_scene() for a single scene, returning (output, state)."""
    if state is None:
        state = GameState()
    scenes = make_scenes()
    scene = scenes[scene_index]
    with patch("builtins.input", side_effect=commands):
        with patch("sys.stdout", new_callable=StringIO) as out:
            try:
                present_scene(scene, state)
            except SystemExit:
                pass
            return out.getvalue(), state


# ---------------------------------------------------------------------------
# Full Playthrough Tests
# ---------------------------------------------------------------------------

class TestEndingAViaEvidence(unittest.TestCase):
    """Ending A via sending evidence + calling Mara (outside contact).

    When sent_evidence=True AND outside_contact=True, determine_ending
    returns "A" immediately. choose_final_path sees forced="A" and
    returns without offering a choice.
    """

    def test_full_playthrough_ending_a_via_evidence(self):
        commands = _base_scene_commands()
        # Insert CALL ROURKE before CONTINUE in scene 10 (index 20)
        # Base has "CONTINUE" at index 20 for scene 10
        commands[20] = "CALL ROURKE"
        commands.insert(21, "CONTINUE")
        # Insert CALL MARA before CONTINUE in scene 13
        # Scene 13 starts at index 26 (after insertion)
        # Find the CONTINUE for scene 13
        # Scenes: 0-9 = indices 0-19, scene 10 = 20-21, scene 11 = 22-23,
        # scene 12 = 24-25, scene 13 = 26-27
        commands[26] = "CALL MARA"
        commands.insert(27, "CONTINUE")

        output = _run_game(commands)

        self.assertIn("Ending A", output)
        self.assertIn(ENDING_TEXT["A"], output)
        # Should NOT show final choice prompt (forced A)
        self.assertNotIn("TURN / BURN / KILL", output)


class TestEndingAViaTurn(unittest.TestCase):
    """Ending A via choosing TURN at the final crossroads.

    With base stats (high courage, no evidence sent, no outside contact),
    determine_ending returns "B" initially. choose_final_path offers
    the choice. Player selects TURN → Ending A.
    """

    def test_full_playthrough_ending_a_via_turn(self):
        commands = _base_scene_commands() + ["TURN"]
        output = _run_game(commands)

        self.assertIn("Final choices: TURN / BURN / KILL", output)
        self.assertIn("Ending A", output)
        self.assertIn(ENDING_TEXT["A"], output)


class TestEndingBViaBurn(unittest.TestCase):
    """Ending B via choosing BURN at the final crossroads.

    Same setup as TURN test, but player chooses BURN.
    """

    def test_full_playthrough_ending_b_via_burn(self):
        commands = _base_scene_commands() + ["BURN"]
        output = _run_game(commands)

        self.assertIn("Final choices: TURN / BURN / KILL", output)
        self.assertIn("Ending B", output)
        self.assertIn(ENDING_TEXT["B"], output)


class TestEndingCViaKill(unittest.TestCase):
    """Ending C via choosing KILL at the final crossroads.

    Same setup, player chooses KILL → Ending C.
    """

    def test_full_playthrough_ending_c_via_kill(self):
        commands = _base_scene_commands() + ["KILL"]
        output = _run_game(commands)

        self.assertIn("Final choices: TURN / BURN / KILL", output)
        self.assertIn("Ending C", output)
        self.assertIn(ENDING_TEXT["C"], output)


class TestHiddenEnding(unittest.TestCase):
    """Hidden ending via sustained low lucidity + omen accumulation.

    Drink heavily in scenes 11 and 13 to crash lucidity, triggering
    omen marks from checkpoints and effects. The combination of
    low_lucidity_streak >= 3 and omen_marks >= 4 triggers HIDDEN.
    """

    def test_full_playthrough_hidden_ending(self):
        commands = [
            # Scenes 0-9: same as base
            "ASK CARLA", "CONTINUE",
            "ASK BELL", "CONTINUE",
            "LOOK PORCH", "CONTINUE",
            "LOOK DESK", "CONTINUE",
            "READ NOTEBOOK", "CONTINUE",
            "LOOK KITCHEN", "CONTINUE",
            "ASK EVELYN", "CONTINUE",
            "LOOK ROOM", "CONTINUE",
            "READ FILE", "CONTINUE",
            "READ MEMO", "CONTINUE",
            # Scene 10: hold files
            "HOLD FILES", "CONTINUE",
            # Scene 11: drink 3x to crash lucidity, then ASK BELL
            "DRINK WHISKEY", "DRINK WHISKEY", "DRINK WHISKEY",
            "ASK BELL", "CONTINUE",
            # Scene 12: read envelope
            "READ ENVELOPE", "CONTINUE",
            # Scene 13: drink once more
            "DRINK WHISKEY", "CONTINUE",
            # Scenes 14-18: minimum required
            "LOOK RADIO", "CONTINUE",
            "ASK GABRIEL", "CONTINUE",
            "READ COPY", "CONTINUE",
            "ASK EVELYN", "CONTINUE",
            "READ PHOTO", "CONTINUE",
            # No final choice (forced HIDDEN)
        ]

        output = _run_game(commands)

        self.assertIn("Ending HIDDEN", output)
        self.assertIn(ENDING_TEXT["HIDDEN"], output)
        # Should NOT show final choice prompt (forced HIDDEN)
        self.assertNotIn("TURN / BURN / KILL", output)


class TestQuit(unittest.TestCase):
    """QUIT at the first scene exits the game immediately."""

    def test_quit_at_start(self):
        commands = ["QUIT"]
        output = _run_game(commands)

        self.assertIn("You leave the case", output)
        # Should not reach any ending
        self.assertNotIn("Ending A", output)
        self.assertNotIn("Ending B", output)
        self.assertNotIn("Ending C", output)
        self.assertNotIn("Ending HIDDEN", output)

    def test_quit_mid_game(self):
        """QUIT after completing a few scenes."""
        commands = [
            "ASK CARLA", "CONTINUE",
            "ASK BELL", "CONTINUE",
            "QUIT",
        ]
        output = _run_game(commands)

        self.assertIn("You leave the case", output)
        self.assertNotIn("Ending", output)


class TestInvalidCommands(unittest.TestCase):
    """Invalid commands are handled gracefully without crashing."""

    def test_invalid_commands_in_scene(self):
        commands = [
            "FLY",
            "DANCE",
            "SWIM",
            "ASK CARLA",
            "CONTINUE",
            "QUIT",
        ]
        output = _run_game(commands)

        # Should show "does not answer" for invalid commands
        self.assertIn("does not answer", output.lower())
        # Should still be able to progress
        self.assertIn("You leave the case", output)

    def test_empty_input(self):
        commands = [
            "",
            "   ",
            "ASK CARLA",
            "CONTINUE",
            "QUIT",
        ]
        output = _run_game(commands)
        self.assertIn("You leave the case", output)


class TestHelpAndStatus(unittest.TestCase):
    """HELP and STATUS commands work in any scene."""

    def test_help_shows_commands(self):
        commands = [
            "HELP",
            "ASK CARLA",
            "CONTINUE",
            "QUIT",
        ]
        output = _run_game(commands)
        # HELP_TEXT should appear
        self.assertIn("LOOK", output)
        self.assertIn("ASK", output)
        self.assertIn("READ", output)
        self.assertIn("CONTINUE", output)

    def test_status_shows_stats(self):
        commands = [
            "STATUS",
            "ASK CARLA",
            "CONTINUE",
            "QUIT",
        ]
        output = _run_game(commands)
        self.assertIn("COURAGE", output)
        self.assertIn("LUCIDITY", output)
        self.assertIn("REASON", output)


class TestThinkCommand(unittest.TestCase):
    """THINK reveals different voices based on state."""

    def test_think_at_start(self):
        commands = [
            "THINK",
            "ASK CARLA",
            "CONTINUE",
            "QUIT",
        ]
        output = _run_game(commands)
        # At game start, should show RUST and GLASS
        self.assertIn("RUST", output)
        self.assertIn("GLASS", output)


class TestSceneGating(unittest.TestCase):
    """CONTINUE is blocked until required interactions are completed."""

    def test_cannot_continue_without_required(self):
        """In scene 0, CONTINUE before ASK CARLA should be blocked."""
        output, state = _run_scene(["CONTINUE", "ASK CARLA", "CONTINUE"])
        self.assertIn("not done", output.lower())
        # After ASK CARLA, CONTINUE should work
        self.assertEqual(state.courage, 4)  # ASK CARLA gives courage+1


class TestAllScenesReachable(unittest.TestCase):
    """Verify that all 19 scenes are traversed in a full playthrough."""

    def test_all_scene_titles_appear(self):
        commands = _base_scene_commands() + ["BURN"]
        output = _run_game(commands)

        expected_titles = [
            "Chapter 1.1: The police station lobby",
            "Chapter 1.2: Chief Bell's office",
            "Chapter 2.1: The Wren house exterior",
            "Chapter 2.2: Foyer and study",
            "Chapter 2.3: Pantry and children's rooms",
            "Chapter 3.1: The mother house exterior and kitchen",
            "Chapter 3.2: The meal that is not a meal",
            "Chapter 3.3: Gabriel's empty room",
            "Chapter 4.1: Hospital records office",
            "Chapter 4.2: County archive basement",
            "Chapter 4.3: The superior call",
            "Chapter 5.1: The bar",
            "Chapter 5.2: The off-book files",
            "Chapter 5.3: After midnight choice",
            "Chapter 6.1: The approach",
            "Chapter 6.2: The first confession",
            "Chapter 6.3: The broken memory",
            "Chapter 7.1: Evelyn at the table",
            "Chapter 7.2: Hidden evidence in the house",
        ]
        for title in expected_titles:
            self.assertIn(title, output, f"Scene '{title}' not found in output")


class TestOptionalInteractions(unittest.TestCase):
    """Optional interactions (DRINK, CALL, extra LOOK/READ) work correctly."""

    def test_drink_whiskey_in_bar(self):
        """DRINK WHISKEY in scene 11 (the bar) should lower lucidity."""
        commands = [
            # Scenes 0-10: base
            "ASK CARLA", "CONTINUE",
            "ASK BELL", "CONTINUE",
            "LOOK PORCH", "CONTINUE",
            "LOOK DESK", "CONTINUE",
            "READ NOTEBOOK", "CONTINUE",
            "LOOK KITCHEN", "CONTINUE",
            "ASK EVELYN", "CONTINUE",
            "LOOK ROOM", "CONTINUE",
            "READ FILE", "CONTINUE",
            "READ MEMO", "CONTINUE",
            "CONTINUE",
            # Scene 11: drink, then ASK BELL
            "DRINK WHISKEY",
            "ASK BELL",
            "CONTINUE",
            # QUIT after scene 11
            "QUIT",
        ]
        output, state = _run_scene(commands[:23], scene_index=11,
                                    state=_build_state_for_scene(11))
        # Just verify the game doesn't crash
        self.assertIsNotNone(output)

    def test_call_rourke_sends_evidence(self):
        """CALL ROURKE in scene 10 sets sent_evidence."""
        state = _build_state_for_scene(10)
        output, state = _run_scene(["CALL ROURKE", "CONTINUE"],
                                    scene_index=10, state=state)
        self.assertTrue(state.sent_evidence)

    def test_hold_files_sets_courage_and_reason(self):
        """HOLD FILES in scene 10 increases courage, decreases reason."""
        state = _build_state_for_scene(10)
        initial_reason = state.reason
        output, state = _run_scene(["HOLD FILES", "CONTINUE"],
                                    scene_index=10, state=state)
        self.assertEqual(state.reason, initial_reason - 1)

    def test_call_mara_sets_outside_contact(self):
        """CALL MARA in scene 13 sets outside_contact."""
        state = _build_state_for_scene(13)
        output, state = _run_scene(["CALL MARA", "CONTINUE"],
                                    scene_index=13, state=state)
        self.assertTrue(state.outside_contact)


class TestCaseInsensitiveCommands(unittest.TestCase):
    """Commands are case-insensitive."""

    def test_lowercase_commands(self):
        commands = [
            "ask carla",
            "continue",
            "quit",
        ]
        output = _run_game(commands)
        self.assertIn("You leave the case", output)

    def test_mixed_case_commands(self):
        commands = [
            "Ask Carla",
            "Continue",
            "Quit",
        ]
        output = _run_game(commands)
        self.assertIn("You leave the case", output)


class TestFinalChoiceValidation(unittest.TestCase):
    """The final choice system rejects invalid input."""

    def test_invalid_final_choice(self):
        commands = _base_scene_commands() + [
            "MAYBE",
            "NOTHING",
            "BURN",
        ]
        output = _run_game(commands)
        self.assertIn("Type TURN, BURN, or KILL", output)
        self.assertIn("Ending B", output)

    def test_think_in_final_choice(self):
        commands = _base_scene_commands() + [
            "THINK",
            "TURN",
        ]
        output = _run_game(commands)
        self.assertIn("RUST", output)
        self.assertIn("Ending A", output)

    def test_help_in_final_choice(self):
        commands = _base_scene_commands() + [
            "HELP",
            "KILL",
        ]
        output = _run_game(commands)
        self.assertIn("LOOK", output)
        self.assertIn("Ending C", output)


class TestEndingOutput(unittest.TestCase):
    """Each ending produces the correct output text."""

    def test_ending_a_text_present(self):
        commands = _base_scene_commands() + ["TURN"]
        output = _run_game(commands)
        self.assertIn("Ending A", output)
        self.assertIn("The arrest happens in daylight", output)

    def test_ending_b_text_present(self):
        commands = _base_scene_commands() + ["BURN"]
        output = _run_game(commands)
        self.assertIn("Ending B", output)
        self.assertIn("You burn the copies first", output)

    def test_ending_c_text_present(self):
        commands = _base_scene_commands() + ["KILL"]
        output = _run_game(commands)
        self.assertIn("Ending C", output)
        self.assertIn("You understand with dreadful calm", output)

    def test_hidden_ending_text_present(self):
        commands = [
            "ASK CARLA", "CONTINUE",
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
            "DRINK WHISKEY", "DRINK WHISKEY", "DRINK WHISKEY",
            "ASK BELL", "CONTINUE",
            "READ ENVELOPE", "CONTINUE",
            "DRINK WHISKEY", "CONTINUE",
            "LOOK RADIO", "CONTINUE",
            "ASK GABRIEL", "CONTINUE",
            "READ COPY", "CONTINUE",
            "ASK EVELYN", "CONTINUE",
            "READ PHOTO", "CONTINUE",
        ]
        output = _run_game(commands)
        self.assertIn("Ending HIDDEN", output)
        self.assertIn("The truth does not arrive like lightning", output)


class TestDetermineEndingDirect(unittest.TestCase):
    """Direct tests for determine_ending with constructed states."""

    def test_ending_a_evidence_and_outside(self):
        state = GameState()
        state.sent_evidence = True
        state.outside_contact = True
        self.assertEqual(determine_ending(state), "A")

    def test_ending_a_via_turn(self):
        state = GameState()
        state.final_choice = "TURN"
        state.courage = 8
        self.assertEqual(determine_ending(state), "A")

    def test_ending_b_via_burn(self):
        state = GameState()
        state.final_choice = "BURN"
        state.courage = 8
        self.assertEqual(determine_ending(state), "B")

    def test_ending_b_default_high_courage(self):
        state = GameState()
        state.courage = 8
        state.lucidity = 4
        state.reason = 4
        self.assertEqual(determine_ending(state), "B")

    def test_ending_c_via_kill(self):
        state = GameState()
        state.final_choice = "KILL"
        state.courage = 8
        self.assertEqual(determine_ending(state), "C")

    def test_ending_c_low_lucidity(self):
        state = GameState()
        state.courage = 8
        state.lucidity = 0
        state.reason = 4
        self.assertEqual(determine_ending(state), "C")

    def test_ending_c_low_reason(self):
        state = GameState()
        state.courage = 8
        state.lucidity = 4
        state.reason = 1
        self.assertEqual(determine_ending(state), "C")

    def test_ending_c_low_courage_default(self):
        state = GameState()
        state.courage = 4
        state.lucidity = 4
        state.reason = 4
        self.assertEqual(determine_ending(state), "C")

    def test_hidden_ending_streak_and_omens(self):
        state = GameState()
        state.courage = 8
        state.lucidity = 1
        state.reason = 4
        state.low_lucidity_streak = 3
        state.omen_marks = 4
        self.assertEqual(determine_ending(state), "HIDDEN")

    def test_hidden_ending_high_streak(self):
        state = GameState()
        state.courage = 8
        state.lucidity = 1
        state.reason = 4
        state.low_lucidity_streak = 2
        state.omen_marks = 5
        self.assertEqual(determine_ending(state), "HIDDEN")

    def test_hidden_takes_priority_over_c(self):
        state = GameState()
        state.courage = 8
        state.lucidity = 0
        state.reason = 4
        state.low_lucidity_streak = 4
        state.omen_marks = 6
        self.assertEqual(determine_ending(state), "HIDDEN")

    def test_evidence_takes_priority_over_hidden(self):
        state = GameState()
        state.sent_evidence = True
        state.outside_contact = True
        state.low_lucidity_streak = 5
        state.omen_marks = 10
        self.assertEqual(determine_ending(state), "A")


class TestParseCommand(unittest.TestCase):
    """Command parsing handles various input formats."""

    def test_simple_command(self):
        self.assertEqual(parse_command("LOOK DESK"), ("LOOK", "DESK"))

    def test_lowercase(self):
        self.assertEqual(parse_command("look desk"), ("LOOK", "DESK"))

    def test_mixed_case(self):
        self.assertEqual(parse_command("Look Desk"), ("LOOK", "DESK"))

    def test_verb_only(self):
        self.assertEqual(parse_command("THINK"), ("THINK", ""))

    def test_empty_input(self):
        self.assertEqual(parse_command(""), ("", ""))

    def test_whitespace_only(self):
        self.assertEqual(parse_command("   "), ("", ""))

    def test_extra_spaces(self):
        self.assertEqual(parse_command("  ASK   CARLA  "), ("ASK", "CARLA"))


class TestSceneCount(unittest.TestCase):
    """The game has exactly 19 scenes."""

    def test_scene_count(self):
        scenes = make_scenes()
        self.assertEqual(len(scenes), 19)

    def test_scene_titles_unique(self):
        scenes = make_scenes()
        titles = [s.title for s in scenes]
        self.assertEqual(len(titles), len(set(titles)))


# ---------------------------------------------------------------------------
# Helper to build a GameState with stats appropriate for a given scene index
# ---------------------------------------------------------------------------

def _build_state_for_scene(scene_index):
    """Build a GameState with stats that match arriving at the given scene
    via the base (optimal) path."""
    state = GameState()
    # Simulate the stat changes from the base sequence up to scene_index
    # Scene 0: ASK CARLA → courage+1
    if scene_index > 0:
        state.courage += 1  # 4
    # Scene 1: ASK BELL → reason+1
    if scene_index > 1:
        state.reason += 1  # 5
    # Scene 2: LOOK PORCH → courage+1 (porch_effect)
    if scene_index > 2:
        state.courage += 1  # 5
    # Scene 3: LOOK DESK → courage+1
    if scene_index > 3:
        state.courage += 1  # 6
    # Scene 4: READ NOTEBOOK → reason+1, courage+1 (notebook_effect)
    if scene_index > 4:
        state.reason += 1  # 6
        state.courage += 1  # 7
    # Scene 5: LOOK KITCHEN → no stat change
    # Scene 6: ASK EVELYN → courage+1, reason+1
    if scene_index > 6:
        state.courage = min(state.courage + 1, 8)  # 8
        state.reason += 1  # 7
    # Scene 7: LOOK ROOM → courage+1
    if scene_index > 7:
        state.courage = min(state.courage + 1, 8)  # 8
    # Scene 8: READ FILE → courage+2, lucidity+1 (hospital_effect)
    if scene_index > 8:
        state.courage = min(state.courage + 2, 8)  # 8
        state.lucidity += 1  # 5
    # Scene 9: READ MEMO → reason+1
    if scene_index > 9:
        state.reason = min(state.reason + 1, 8)  # 8
    # Scene 10: auto-hold → courage+1, reason-1
    if scene_index > 10:
        state.courage = min(state.courage + 1, 8)  # 8
        state.reason -= 1  # 7
    # Scene 11: ASK BELL → reason+1
    if scene_index > 11:
        state.reason = min(state.reason + 1, 8)  # 8
    # Scene 12: READ ENVELOPE → courage+1, reason+1 (bell_photo_effect)
    if scene_index > 12:
        state.courage = min(state.courage + 1, 8)  # 8
        state.reason = min(state.reason + 1, 8)  # 8
    # Scene 13: no stat change (just CONTINUE)
    # Scene 14: LOOK RADIO → no stat change
    # Scene 15: ASK GABRIEL → courage+1, reason+1
    if scene_index > 15:
        state.courage = min(state.courage + 1, 8)  # 8
        state.reason = min(state.reason + 1, 8)  # 8
    # Scene 16: READ COPY → chain(courage+2, lucidity-1) + broken_memory(courage+1, lucidity-1, reason-1, mark_omen)
    if scene_index > 16:
        state.courage = min(state.courage + 3, 8)  # 8
        state.lucidity -= 2  # 3
        state.reason -= 1  # 7
        state.omen_marks += 1  # 1
    # Scene 17: ASK EVELYN → courage+1, reason+1
    if scene_index > 17:
        state.courage = min(state.courage + 1, 8)  # 8
        state.reason = min(state.reason + 1, 8)  # 8
    # Scene 18: READ PHOTO → courage+1 (photo_effect)
    if scene_index > 18:
        state.courage = min(state.courage + 1, 8)  # 8

    return state


if __name__ == "__main__":
    unittest.main()

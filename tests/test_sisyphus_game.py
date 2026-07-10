import unittest


from sisyphus_game import (
    GameState,
    build_think_text,
    determine_ending,
    make_scenes,
    parse_command,
    run_scene_command,
)


class EndingLogicTests(unittest.TestCase):
    def test_lawful_betrayal_overrides_other_outcomes(self):
        state = GameState(
            courage=7,
            lucidity=4,
            reason=4,
            sent_evidence=True,
            outside_contact=True,
            low_lucidity_streak=0,
        )

        self.assertEqual(determine_ending(state), "A")

    def test_hidden_ending_triggers_after_long_low_lucidity_streak(self):
        state = GameState(
            courage=5,
            lucidity=2,
            reason=2,
            sent_evidence=False,
            outside_contact=False,
            low_lucidity_streak=3,
            omen_marks=4,
        )

        self.assertEqual(determine_ending(state), "HIDDEN")

    def test_hidden_ending_can_become_inevitable_through_omens_before_total_collapse(self):
        state = GameState(
            courage=4,
            lucidity=2,
            reason=2,
            sent_evidence=False,
            outside_contact=False,
            low_lucidity_streak=2,
            omen_marks=5,
        )

        self.assertEqual(determine_ending(state), "HIDDEN")

    def test_blood_inheritance_triggers_when_reason_or_lucidity_crashes(self):
        state = GameState(
            courage=6,
            lucidity=1,
            reason=4,
            sent_evidence=False,
            outside_contact=False,
            low_lucidity_streak=1,
        )

        self.assertEqual(determine_ending(state), "C")

    def test_family_silence_requires_courage(self):
        state = GameState(
            courage=6,
            lucidity=4,
            reason=4,
            sent_evidence=False,
            outside_contact=False,
            low_lucidity_streak=0,
        )

        self.assertEqual(determine_ending(state), "B")

    def test_checkpoint_updates_low_lucidity_streak(self):
        state = GameState(
            courage=3,
            lucidity=2,
            reason=3,
            sent_evidence=False,
            outside_contact=False,
            low_lucidity_streak=0,
        )

        state.register_checkpoint()
        self.assertEqual(state.low_lucidity_streak, 1)

        state.lucidity = 4
        state.register_checkpoint()
        self.assertEqual(state.low_lucidity_streak, 0)


class CommandSystemTests(unittest.TestCase):
    def _find_scene_with_command(self, verb, target):
        for scene in make_scenes():
            if (verb, target) in scene.interactions:
                return scene
        self.fail(f"Could not find scene with command {(verb, target)}")

    def test_story_is_split_into_many_subscenes(self):
        scenes = make_scenes()

        self.assertGreaterEqual(len(scenes), 14)
        self.assertIn("1.1", scenes[0].title)

    def test_parse_command_splits_verb_and_target(self):
        self.assertEqual(parse_command("look desk"), ("LOOK", "DESK"))

    def test_parse_command_keeps_single_word_verbs(self):
        self.assertEqual(parse_command("think"), ("THINK", ""))

    def test_continue_is_blocked_until_required_actions_are_done(self):
        state = GameState()
        scene = make_scenes()[0]

        result = run_scene_command(scene, state, "CONTINUE")

        self.assertEqual(result.status, "stay")
        self.assertIn("not done", result.text.lower())

    def test_look_command_returns_environment_text(self):
        state = GameState()
        scene = make_scenes()[0]

        result = run_scene_command(scene, state, "LOOK LOBBY")

        self.assertEqual(result.status, "stay")
        self.assertIn("bleach", result.text.lower())

    def test_call_command_can_mark_outside_contact(self):
        state = GameState()
        scene = self._find_scene_with_command("CALL", "MARA")

        result = run_scene_command(scene, state, "CALL MARA")

        self.assertEqual(result.status, "stay")
        self.assertTrue(state.outside_contact)
        self.assertIn("mara", result.text.lower())

    def test_drink_command_reduces_lucidity(self):
        state = GameState()
        scene = self._find_scene_with_command("DRINK", "WHISKEY")
        starting_lucidity = state.lucidity

        result = run_scene_command(scene, state, "DRINK WHISKEY")

        self.assertEqual(result.status, "stay")
        self.assertLess(state.lucidity, starting_lucidity)

    def test_think_text_gains_distortion_when_lucidity_is_low(self):
        state = GameState(lucidity=1, omen_marks=3)
        scene = make_scenes()[0]

        think_text = build_think_text(scene, state)

        self.assertIn("RUST:", think_text)
        self.assertIn("GLASS:", think_text)
        self.assertIn("MUD:", think_text)
        self.assertIn("CHOIR:", think_text)
        self.assertIn("badge", think_text.lower())

    def test_drinking_on_low_lucidity_path_accumulates_hidden_ending_omens(self):
        state = GameState(lucidity=2)
        scene = self._find_scene_with_command("DRINK", "WHISKEY")

        run_scene_command(scene, state, "DRINK WHISKEY")
        run_scene_command(scene, state, "DRINK WHISKEY")

        self.assertGreaterEqual(state.omen_marks, 1)


if __name__ == "__main__":
    unittest.main()

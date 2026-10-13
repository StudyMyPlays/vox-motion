import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import script_check  # noqa: E402


class ScriptCheckTest(unittest.TestCase):
    def test_template_passes(self):
        source = (ROOT / "assets" / "script-template.md").read_text(encoding="utf-8")
        blocks, problems = script_check.check_script(source, expected_blocks=6)
        self.assertEqual(problems, [])
        self.assertEqual(len(blocks), 6)
        self.assertTrue(all(not b.errors for b in blocks))

    def test_digits_are_errors(self):
        blocks, _ = script_check.check_script(
            "Block 1: In 2024 the price of eggs rose seventy percent, and nobody in the grocery business saw it coming at all."
        )
        self.assertTrue(any("digits" in e for e in blocks[0].errors))

    def test_stage_directions_are_errors(self):
        blocks, _ = script_check.check_script(
            "Block 1: (pause) Every day humans throw away enough food to feed two billion people, and most never reaches a plate."
        )
        self.assertTrue(any("brackets" in e for e in blocks[0].errors))

    def test_numbering_and_count(self):
        text = "Block 1: one two three.\nBlock 3: four five six."
        _, problems = script_check.check_script(text, expected_blocks=3)
        self.assertTrue(any("1..N" in p for p in problems))
        self.assertTrue(any("expected 3" in p for p in problems))

    def test_continuation_lines_and_comments(self):
        text = "<!-- Block 9: ignored -->\nBlock 1: first half of the line\ncontinues here."
        blocks, problems = script_check.check_script(text)
        self.assertEqual(problems, [])
        self.assertEqual(blocks[0].text, "first half of the line continues here.")

    def test_sentence_breaks_add_time(self):
        one = script_check.estimate_seconds("a b c d e f g h i j, k l m n o p q r s t.")
        two = script_check.estimate_seconds("a b c d e f g h i j. k l m n o p q r s t.")
        self.assertAlmostEqual(two - one, script_check.SENTENCE_PAUSE_SEC)

    def test_greeting_warning(self):
        blocks, _ = script_check.check_script(
            "Block 1: Welcome back, in this video we look at why food waste is really a story about trucks and fridges."
        )
        self.assertTrue(any("greeting" in w for w in blocks[0].warnings))


if __name__ == "__main__":
    unittest.main()

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import prompt_lint  # noqa: E402

DIORAMA_OK = """Block 1
cinematic vintage paper diorama, aged sepia newsprint world, non-photorealistic,
no live-action — shot as ONE continuous high-energy FPV camera move.
The shot: a burnt-orange stamp punches "EXPIRED" across a treaty page.
Sound design: <guillotine slam> <page rip>. No speech.
No text anywhere except "EXPIRED". No gibberish letters, no captions.
"""


def worked_examples():
    """The Mixed Media worked examples in references/vox-prompts.md, renumbered 1..N."""
    text = (ROOT / "references" / "vox-prompts.md").read_text(encoding="utf-8")
    bodies = re.findall(r"```\nBlock \d+\n(.*?)```", text, re.S)
    return "\n".join(f"Block {i}\n{body}" for i, body in enumerate(bodies, start=1)), len(bodies)


class MixedLintTest(unittest.TestCase):
    def test_reference_worked_examples_pass_clean(self):
        source, count = worked_examples()
        self.assertGreaterEqual(count, 2)
        prompts, problems = prompt_lint.lint(source, "mixed", expected_blocks=count)
        self.assertEqual(problems, [])
        for p in prompts:
            self.assertEqual(p.errors, [], f"block {p.number}")
            self.assertEqual(p.warnings, [], f"block {p.number}")

    def test_missing_labels_and_text_asks(self):
        source = "Block 1\nSTYLE REFERENCE: collage.\nSCENE: a headline slams in.\n"
        prompts, _ = prompt_lint.lint(source, "mixed")
        errors = " ".join(prompts[0].errors)
        self.assertIn("MOTION:", errors)
        self.assertIn("NEGATIVE:", errors)
        self.assertIn("readable text", errors)
        self.assertIn("non-photorealistic", errors)

    def test_moderation_and_dialogue(self):
        source, _ = worked_examples()
        source = source.replace("SCENE:", "SCENE: a mushroom cloud rises; {Hello.}", 1)
        prompts, _ = prompt_lint.lint(source, "mixed")
        errors = " ".join(prompts[0].errors)
        self.assertIn("mushroom cloud", errors)
        self.assertIn("dialogue braces", errors)

    def test_params_in_prompt_warn(self):
        source, _ = worked_examples()
        source = source.replace("MOTION:", "MOTION: 9:16 vertical,", 1)
        prompts, _ = prompt_lint.lint(source, "mixed")
        self.assertTrue(any("parameters" in w for w in prompts[0].warnings))


class DioramaLintTest(unittest.TestCase):
    def test_fenced_label_passes(self):
        prompts, problems = prompt_lint.lint(DIORAMA_OK, "diorama", expected_blocks=1)
        self.assertEqual(problems, [])
        self.assertEqual(prompts[0].errors, [])

    def test_unfenced_label_and_missing_no_speech(self):
        source = DIORAMA_OK.replace("No speech.", "").replace('"EXPIRED" across', '"EXPIRED" and "TREATY" across')
        prompts, _ = prompt_lint.lint(source, "diorama")
        errors = " ".join(prompts[0].errors)
        self.assertIn("No speech", errors)
        self.assertIn("TREATY", errors)


if __name__ == "__main__":
    unittest.main()

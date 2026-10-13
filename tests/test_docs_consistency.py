import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "SKILL.md", ROOT / "README.md", *sorted((ROOT / "references").glob("*.md"))]
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
BACKTICK_PATH = re.compile(r"`((?:references|assets|scripts)/[\w.\-/]+)`")


class DocsConsistencyTest(unittest.TestCase):
    def test_relative_links_resolve(self):
        for doc in DOCS:
            for target in LINK.findall(doc.read_text(encoding="utf-8")):
                if re.match(r"^[a-z]+:", target):
                    continue
                with self.subTest(doc=doc.name, target=target):
                    self.assertTrue((doc.parent / target).exists(), f"{doc.name} -> {target}")

    def test_backticked_repo_paths_exist(self):
        for doc in DOCS:
            for target in BACKTICK_PATH.findall(doc.read_text(encoding="utf-8")):
                with self.subTest(doc=doc.name, target=target):
                    self.assertTrue((ROOT / target).exists(), f"{doc.name} -> {target}")

    def test_skill_frontmatter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match)
        front = match.group(1)
        self.assertRegex(front, r"(?m)^name: vox-motion$")
        self.assertIn("description:", front)

    def test_skill_keeps_core_contract(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for needle in ("80e4dd7b-cd65-42d4-b191-b58d62558602", "aspect_ratio", "explainer_video",
                       "declined_preset_id", "list_voices", "resolve_explainer_preset"):
            self.assertIn(needle, text)

    def test_examples_parse(self):
        manifest = json.loads((ROOT / "assets" / "run-manifest.example.json").read_text(encoding="utf-8"))
        self.assertEqual([i["block"] for i in manifest["items"]], list(range(1, manifest["blocks"] + 1)))
        evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual(evals["skill_name"], "vox-motion")
        self.assertTrue(all(e["prompt"] and e["expected_output"] for e in evals["evals"]))


if __name__ == "__main__":
    unittest.main()

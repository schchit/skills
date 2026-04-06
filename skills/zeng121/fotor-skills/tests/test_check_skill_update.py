import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_skill_update.py"
SPEC = importlib.util.spec_from_file_location("check_skill_update", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class CheckSkillUpdateTests(unittest.TestCase):
    def test_read_local_skill_metadata_uses_top_level_version(self) -> None:
        metadata = MODULE.read_local_skill_metadata()
        self.assertEqual(metadata["version"], "1.0.11")

    def test_read_local_skill_metadata_falls_back_to_metadata_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_md = root / "SKILL.md"
            skill_md.write_text(
                "---\n"
                "name: sample-skill\n"
                "metadata:\n"
                "  version: 0.9.0\n"
                "  author: sample-author\n"
                "---\n",
                encoding="utf-8",
            )

            original_root = MODULE.ROOT
            original_skill_md_path = MODULE.SKILL_MD_PATH
            try:
                MODULE.ROOT = root
                MODULE.SKILL_MD_PATH = skill_md
                metadata = MODULE.read_local_skill_metadata()
            finally:
                MODULE.ROOT = original_root
                MODULE.SKILL_MD_PATH = original_skill_md_path

        self.assertEqual(metadata["slug"], "sample-skill")
        self.assertEqual(metadata["version"], "0.9.0")
        self.assertEqual(metadata["author"], "sample-author")


if __name__ == "__main__":
    unittest.main()

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
CONTRACTS = ROOT / ".agents" / "contracts"
BIASED_TERMS = re.compile(
    r"\b(filipino|filipina|philippines?|pinoy|pinay|tagalog|taglish|manila|cebu|"
    r"morena|teleserye|sampal|kabit|barong|unilab|unilever|jollibee|puregold|"
    r"paksiw|adobo|sinigang|lechon|calamansi|jeepney|barangay|lola|lolo)\b",
    re.IGNORECASE,
)
EXCLUDED_SKILLS = re.compile(
    r"seedance-prompt-25-filipino|filipino-micro-drama|blender-to-seedance|"
    r"seedance-graybox-world|seed-audio-15-api|seed-audio-prompt-15|"
    r"blender-mcp-setup"
)
CONFIDENTIAL = re.compile(r"seed audio 1\.5|larkoffice\.com|higgsfield", re.IGNORECASE)
EXAMPLE_SERIES = (
    SKILLS / "seedream-woodblock-poster" / "examples",
    SKILLS / "seedream-handcrafted-3d" / "examples",
)
LANGUAGE_DATA = {
    SKILLS / "audio-dubbing" / "references" / "language-reference.md",
    SKILLS / "audio-dubbing" / "references" / "extended-dubbing.md",
    SKILLS / "seedream-prompt" / "references" / "image-generation.md",
    SKILLS / "seedream-prompt" / "references" / "quick-reference.md",
}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".html", ".txt"}


def tracked_text_files():
    roots = [SKILLS, CONTRACTS, ROOT / "README.md", ROOT / "AGENTS.md"]
    for root in roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if path.is_file() and path.suffix in TEXT_SUFFIXES and "__pycache__" not in path.parts:
                yield path


def offenders(pattern, allowed_dirs=(), allowed_files=frozenset()):
    found = []
    for path in tracked_text_files():
        if path in allowed_files or any(directory in path.parents for directory in allowed_dirs):
            continue
        for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if pattern.search(line):
                found.append(f"{path.relative_to(ROOT)}:{number}")
    return found


class MarketNeutralityTests(unittest.TestCase):
    def test_skills_and_contracts_do_not_assume_a_market(self):
        self.assertEqual(offenders(BIASED_TERMS, EXAMPLE_SERIES, LANGUAGE_DATA), [])

    def test_no_reference_to_skills_outside_this_repository(self):
        self.assertEqual(offenders(EXCLUDED_SKILLS), [])

    def test_no_confidential_models_internal_links_or_competitor_names(self):
        self.assertEqual(offenders(CONFIDENTIAL), [])


if __name__ == "__main__":
    unittest.main()

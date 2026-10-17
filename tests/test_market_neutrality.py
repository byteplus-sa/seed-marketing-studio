import hashlib
import re
import unittest
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
CONTRACTS = ROOT / ".agents" / "contracts"
CATALOG = ROOT / ".agents" / "catalog"
TESTS = ROOT / "tests"
BIASED_TERMS = re.compile(
    r"\b(filipino|filipina|philippines?|pinoy|pinay|tagalog|taglish|manila|cebu|"
    r"morena|teleserye|sampal|kabit|barong|"
    r"paksiw|adobo|sinigang|lechon|calamansi|jeepney|barangay|lola|lolo)\b",
    re.IGNORECASE,
)
EXCLUDED_SKILLS = re.compile(
    r"seedance-prompt-25-filipino|filipino-micro-drama|blender-to-seedance|"
    r"seedance-graybox-world|blender-mcp-setup"
)
RESTRICTED_TERM_HASHES = frozenset(
    {
        "2b7c080f7b62bce2f78df2a8cd1bdbd1ad78f1d8f6a1b8a59f18632a3f34d1f3",
        "3c67dda6df9cd1a970aa30ed43bb585358fd7580b80b8d3a655edd756475a886",
        "4160708c43542747683cafc5efa43991f06aacd103d451ae4dbb33970b96006c",
        "4a4820d351d3af27176f9bdb8ffe987b8c829057a8bd3e7f9812c25c4a9fd465",
        "50b2676afbe30c833f43fedf384f115302474c88365501ad94ba93aec48777c6",
        "570b8bb5aecb12755a9952c047613df6055e0ffad61eff0c35ff628ce5fbb27f",
        "59e2d3e4258d7184461084c69ebbedb0986ec0a76ff9da00301ca2774ae2e591",
        "6484b97cb46c738a0620525c331f0985adcf31a633d2aeb30166dbc9e7cc478f",
        "768652f9bccee02440617516224b4745d1261a1b6c8d2e5a44ae27e24ef18948",
        "7f0957984e30326a288b3b81288978230af856eb8020b1a0e8b3a138a9ebb7e4",
        "9e58e55216cd54673ead1d43acaf3858a3b23a80fb0f93fc80f9646f6e199a8e",
        "a38c2d7bfc423b198f0e188e4d988bc1b8e8c107a760f9f66a2fc7e9b5b4ede5",
        "c0309d4739981e43e144a253ecf6f74543b8e31714ada1d645d0070d98312c6d",
        "e12c3374d4cc4b6bf4fd8af92537ad45734c5240ffaa33c956da965ac24822bc",
        "e181b3dfcbf4b938b8254b8383c8fc0e4f1e812f6053e09abedf8034732e113c",
    }
)
RESTRICTED_FIRST_WORD_HASHES = frozenset(
    {
        "19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b",
        "2b7c080f7b62bce2f78df2a8cd1bdbd1ad78f1d8f6a1b8a59f18632a3f34d1f3",
        "4160708c43542747683cafc5efa43991f06aacd103d451ae4dbb33970b96006c",
        "50b2676afbe30c833f43fedf384f115302474c88365501ad94ba93aec48777c6",
        "570b8bb5aecb12755a9952c047613df6055e0ffad61eff0c35ff628ce5fbb27f",
        "59e2d3e4258d7184461084c69ebbedb0986ec0a76ff9da00301ca2774ae2e591",
        "6484b97cb46c738a0620525c331f0985adcf31a633d2aeb30166dbc9e7cc478f",
        "7f0957984e30326a288b3b81288978230af856eb8020b1a0e8b3a138a9ebb7e4",
        "89a2fc97c906d37f58d7cfb11d77b20e03e173f013031c6ed65577d2a4ef0ca6",
        "9e58e55216cd54673ead1d43acaf3858a3b23a80fb0f93fc80f9646f6e199a8e",
        "a38c2d7bfc423b198f0e188e4d988bc1b8e8c107a760f9f66a2fc7e9b5b4ede5",
        "e12c3374d4cc4b6bf4fd8af92537ad45734c5240ffaa33c956da965ac24822bc",
        "e181b3dfcbf4b938b8254b8383c8fc0e4f1e812f6053e09abedf8034732e113c",
    }
)
LONGEST_RESTRICTED_TERM = 4
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
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".html", ".css", ".txt"}


def text_files(roots):
    for root in roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if path.is_file() and path.suffix in TEXT_SUFFIXES and "__pycache__" not in path.parts:
                yield path


def generic_files():
    return text_files([SKILLS, CONTRACTS, ROOT / "README.md", ROOT / "AGENTS.md"])


def public_files():
    return text_files([SKILLS, CONTRACTS, CATALOG, TESTS, ROOT / "README.md", ROOT / "AGENTS.md"])


def offenders(pattern, allowed_dirs=(), allowed_files=frozenset()):
    found = []
    for path in generic_files():
        if path in allowed_files or any(directory in path.parents for directory in allowed_dirs):
            continue
        for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if pattern.search(line):
                found.append(f"{path.relative_to(ROOT)}:{number}")
    return found


@cache
def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def words(line):
    return re.sub(r"[^a-z0-9]+", " ", line.lower()).split()


def contains_restricted_term(
    line, term_hashes=RESTRICTED_TERM_HASHES, first_word_hashes=RESTRICTED_FIRST_WORD_HASHES
):
    tokens = words(line)
    for start, token in enumerate(tokens):
        if digest(token) not in first_word_hashes:
            continue
        for length in range(1, LONGEST_RESTRICTED_TERM + 1):
            if digest(" ".join(tokens[start : start + length])) in term_hashes:
                return True
    return False


def restricted_offenders():
    found = []
    for path in public_files():
        for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
            if contains_restricted_term(line):
                found.append(f"{path.relative_to(ROOT)}:{number}")
    return found


class MarketNeutralityTests(unittest.TestCase):
    def test_skills_and_contracts_do_not_assume_a_market(self):
        self.assertEqual(offenders(BIASED_TERMS, EXAMPLE_SERIES, LANGUAGE_DATA), [])

    def test_no_reference_to_skills_outside_this_repository(self):
        self.assertEqual(offenders(EXCLUDED_SKILLS), [])

    def test_no_restricted_names_in_public_files(self):
        self.assertEqual(restricted_offenders(), [])

    def test_restricted_matcher_ignores_case_and_punctuation(self):
        terms = frozenset({digest("zebra crossing 2 0")})
        first = frozenset({digest("zebra")})
        self.assertTrue(contains_restricted_term("See Zebra-Crossing 2.0 here", terms, first))
        self.assertTrue(contains_restricted_term("zebra_crossing_2_0", terms, first))
        self.assertFalse(contains_restricted_term("zebra crossing 3.0", terms, first))
        self.assertFalse(contains_restricted_term("A plain sentence about product shots."))


if __name__ == "__main__":
    unittest.main()

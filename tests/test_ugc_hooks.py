import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "ugc-ad-modes"
REFERENCES = SKILL / "references"
ENTRY = re.compile(r"^### (?P<name>.+?) <!-- id: (?P<id>[a-z0-9-]+) -->$")
FIELD = re.compile(r"^- \*\*(?P<field>[^:*]+):\*\*\s*(?P<value>.*)$")
MODE = re.compile(r"^- `(?P<mode>[a-z0-9-]+)`:", re.MULTILINE)
BEAT_TIMESTAMP = re.compile(r"\bAt (\d+(?:\.\d+)?)-(\d+(?:\.\d+)?) s\b")
MARKET_TERMS = re.compile(
    r"\b(american|british|european|asian|african|latin|chinese|japanese|korean|"
    r"indian|indonesian|thai|vietnamese|malaysian|filipino|philippines?|mexican|"
    r"brazilian|spanish|french|german|arabic|english|tagalog|taglish|usa|uk|"
    r"us market|western|eastern)\b",
    re.IGNORECASE,
)
HOOK_FIELDS = ("Job", "Valid modes", "Seedance beat (0–2 s)", "Audio", "Risks", "Evidence")
SETTING_FIELDS = ("Location", "Light", "Valid modes", "Risks")
FORMULA_FIELDS = ("Evidence", "Use when")


def parse_entries(text):
    entries = []
    current = None
    last_field = ""
    for line in text.splitlines():
        heading = ENTRY.match(line)
        if heading:
            current = {"id": heading["id"], "name": heading["name"], "fields": {}, "lines": [line]}
            entries.append(current)
            continue
        if line.startswith("#"):
            current = None
            continue
        if current is None:
            continue
        current["lines"].append(line)
        field = FIELD.match(line)
        if field:
            last_field = field["field"]
            current["fields"][last_field] = field["value"]
        elif line.startswith("  ") and current["fields"]:
            current["fields"][last_field] = f"{current['fields'][last_field]} {line.strip()}".strip()
    return entries


def section_entries(text, heading):
    start = text.index(heading)
    following = text.find("\n## ", start + len(heading))
    return parse_entries(text[start:] if following == -1 else text[start:following])


def duplicate_ids(entries):
    seen = set()
    duplicates = []
    for entry in entries:
        if entry["id"] in seen:
            duplicates.append(entry["id"])
        seen.add(entry["id"])
    return duplicates


def missing_fields(entries, required):
    return [(entry["id"], field) for entry in entries for field in required if not entry["fields"].get(field)]


def invalid_modes(entries, modes):
    found = []
    for entry in entries:
        listed = [mode.strip() for mode in entry["fields"].get("Valid modes", "").split(",")]
        found.extend((entry["id"], mode) for mode in listed if mode not in modes)
    return found


def skill_modes():
    return set(MODE.findall((SKILL / "SKILL.md").read_text()))


class EntryParserTests(unittest.TestCase):
    def test_parses_fields_and_stops_at_next_heading(self):
        text = (
            "### Alpha <!-- id: hook-alpha -->\n- **Job:** stop\n- **Valid modes:** ugc\n"
            "## Group\nloose text\n### Beta <!-- id: hook-beta -->\n- **Job:** go\n"
        )
        entries = parse_entries(text)
        self.assertEqual([entry["id"] for entry in entries], ["hook-alpha", "hook-beta"])
        self.assertEqual(entries[0]["fields"], {"Job": "stop", "Valid modes": "ugc"})
        self.assertNotIn("loose text", "\n".join(entries[0]["lines"]))

    def test_empty_text_has_no_entries(self):
        self.assertEqual(parse_entries(""), [])

    def test_heading_without_id_is_not_an_entry(self):
        self.assertEqual(parse_entries("### Alpha\n- **Job:** stop\n"), [])

    def test_duplicate_ids_are_reported(self):
        entries = parse_entries("### A <!-- id: x -->\n### B <!-- id: x -->\n### C <!-- id: y -->\n")
        self.assertEqual(duplicate_ids(entries), ["x"])

    def test_wrapped_field_lines_are_joined(self):
        entries = parse_entries("### A <!-- id: a -->\n- **Risks:** first part\n  second part\n")
        self.assertEqual(entries[0]["fields"]["Risks"], "first part second part")

    def test_missing_and_empty_fields_are_reported(self):
        entries = parse_entries("### A <!-- id: a -->\n- **Job:**\n- **Audio:** room tone\n")
        self.assertEqual(missing_fields(entries, ("Job", "Audio", "Risks")), [("a", "Job"), ("a", "Risks")])

    def test_unknown_modes_are_reported(self):
        entries = parse_entries("### A <!-- id: a -->\n- **Valid modes:** ugc, radio-spot\n")
        self.assertEqual(invalid_modes(entries, {"ugc"}), [("a", "radio-spot")])


class HookLibraryTests(unittest.TestCase):
    def setUp(self):
        self.text = (REFERENCES / "hooks.md").read_text()
        self.entries = parse_entries(self.text)
        self.modes = skill_modes()

    def test_skill_declares_nine_modes(self):
        self.assertEqual(len(self.modes), 9)

    def test_about_twelve_hooks_with_unique_prefixed_ids(self):
        self.assertGreaterEqual(len(self.entries), 10)
        self.assertEqual(duplicate_ids(self.entries), [])
        self.assertTrue(all(entry["id"].startswith("hook-") for entry in self.entries))

    def test_hooks_are_grouped_into_stunt_and_subtle(self):
        self.assertGreaterEqual(len(section_entries(self.text, "## Stunt hooks")), 2)
        self.assertGreaterEqual(len(section_entries(self.text, "## Subtle hooks")), 8)

    def test_every_hook_has_required_fields(self):
        self.assertEqual(missing_fields(self.entries, HOOK_FIELDS), [])

    def test_valid_modes_are_real_mode_ids(self):
        self.assertEqual(invalid_modes(self.entries, self.modes), [])

    def test_seedance_beat_is_timestamped_within_opening(self):
        for entry in self.entries:
            stamps = BEAT_TIMESTAMP.findall(entry["fields"]["Seedance beat (0–2 s)"])
            self.assertTrue(stamps, entry["id"])
            self.assertTrue(all(float(end) <= 3 for _, end in stamps), entry["id"])

    def test_no_hook_entry_mentions_a_specific_market(self):
        offenders = [entry["id"] for entry in self.entries if MARKET_TERMS.search("\n".join(entry["lines"]))]
        self.assertEqual(offenders, [])

    def test_testimony_hooks_require_real_or_fictional_disclosure(self):
        for hook_id in ("hook-social-proof", "hook-skeptic-turned-believer"):
            entry = next(entry for entry in self.entries if entry["id"] == hook_id)
            self.assertRegex(entry["fields"]["Risks"], r"approved")

    def test_product_interrupt_stays_silent_until_the_product_stops(self):
        entry = next(entry for entry in self.entries if entry["id"] == "hook-product-interrupt")
        beat = entry["fields"]["Seedance beat (0–2 s)"]
        self.assertIn("silently", beat.split("At 1.5-2 s")[0])
        self.assertIn("no speech until", entry["fields"]["Audio"])

    def test_platform_evidence_quotes_the_guide_and_dates_the_one_pager(self):
        self.assertNotIn("relatable opener", self.text)
        self.assertIn('"Reveal a transformation or surprise visual"', self.text)
        self.assertIn("May 2023", self.text)
        self.assertIn("workspace", self.text.split("## Evidence")[0])

    def test_testimony_wording_matches_the_compliance_contract(self):
        self.assertNotIn("clearly fictional to the viewer", self.text)
        self.assertIn("never framed as a real customer", self.text)
        self.assertIn("no blanket prohibition on AI avatars", self.text)

    def test_library_states_hook_scope_and_exclusivity(self):
        self.assertIn("never", self.text.split("## Evidence")[0].lower())
        self.assertIn("mutually exclusive", self.text)
        self.assertIn("no official benchmark", self.text.lower())


class SettingLibraryTests(unittest.TestCase):
    def setUp(self):
        self.text = (REFERENCES / "settings.md").read_text()
        self.entries = parse_entries(self.text)

    def test_unique_prefixed_ids(self):
        self.assertEqual(duplicate_ids(self.entries), [])
        self.assertTrue(all(entry["id"].startswith("setting-") for entry in self.entries))

    def test_eight_realistic_and_six_heightened(self):
        self.assertEqual(len(section_entries(self.text, "## Realistic settings")), 8)
        self.assertEqual(len(section_entries(self.text, "## Heightened and surreal settings")), 6)

    def test_every_setting_has_required_fields_and_real_modes(self):
        self.assertEqual(missing_fields(self.entries, SETTING_FIELDS), [])
        self.assertEqual(invalid_modes(self.entries, skill_modes()), [])

    def test_no_setting_entry_mentions_a_specific_market(self):
        offenders = [entry["id"] for entry in self.entries if MARKET_TERMS.search("\n".join(entry["lines"]))]
        self.assertEqual(offenders, [])


class ScriptFormulaTests(unittest.TestCase):
    def setUp(self):
        self.entries = parse_entries((REFERENCES / "script-formulas.md").read_text())

    def test_unique_ids_and_required_fields(self):
        self.assertGreaterEqual(len(self.entries), 6)
        self.assertEqual(duplicate_ids(self.entries), [])
        self.assertEqual(missing_fields(self.entries, FORMULA_FIELDS), [])

    def test_every_formula_has_a_placement_timing_table(self):
        for entry in self.entries:
            body = "\n".join(entry["lines"])
            self.assertIn("| 6 s bumper | 15 s | 30 s |", body, entry["id"])
            self.assertRegex(body, r"(?m)^\|[^|\n]*CTA[^|\n]*\|", entry["id"])

    def test_official_formula_cites_a_dated_platform_source(self):
        entry = next(entry for entry in self.entries if entry["id"] == "formula-hook-proposition-cta")
        self.assertIn("Creative_Codes_One_Pager_CA.pdf", entry["fields"]["Evidence"])
        self.assertIn("May 2023", entry["fields"]["Evidence"])

    def test_testimonial_formula_is_not_read_as_an_avatar_ban(self):
        text = (REFERENCES / "script-formulas.md").read_text()
        self.assertIn("no blanket prohibition on AI-generated avatars", text)
        self.assertIn("Not legal advice; re-verify", text)

    def test_evidence_is_labelled(self):
        for entry in self.entries:
            self.assertRegex(entry["fields"]["Evidence"], r"^(official|practitioner)", entry["id"])


class SkillLinkTests(unittest.TestCase):
    def test_skill_links_each_library(self):
        skill = (SKILL / "SKILL.md").read_text()
        for name in ("hooks.md", "settings.md", "script-formulas.md"):
            self.assertIn(f"(references/{name})", skill)


if __name__ == "__main__":
    unittest.main()

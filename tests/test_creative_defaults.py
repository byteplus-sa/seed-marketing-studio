from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"


def normalized(path: Path) -> str:
    return " ".join(path.read_text().lower().split())


class CreativeDefaultsTests(unittest.TestCase):
    def test_action_frequency_checks_use_feasibility_not_count_alone(self):
        paths = (
            "seedance-prompt-25/references/scene-action.md",
            "prompt-review/references/checklist-seedance-25.md",
        )
        for relative in paths:
            with self.subTest(path=relative):
                text = normalized(SKILLS / relative)
                self.assertNotIn("never** demand impossible frequencies", text)
                self.assertNotIn('e.g., "complete three actions in one second"', text)
                self.assertIn("not a fixed action-count threshold", text)
                self.assertIn("genuine timing conflicts or missing inputs", text)
                self.assertIn("readability", text)
                self.assertIn("source", text)
                self.assertIn("optional repair", text)

    def test_lunge_eval_preserves_requested_end_hold_without_requiring_pre_hold(self):
        cases = json.loads(
            (SKILLS / "seedance-acting-console/evals/evals.json").read_text()
        )["evals"]
        case = next(case for case in cases if case["id"] == 10)
        self.assertIn("suddenly lunges", case["prompt"])
        self.assertIn("to hold a needle at a young man's neck", case["prompt"])
        self.assertIn("Keep the veil.", case["prompt"])
        text = " ".join([case["expected_output"], *case["expectations"]]).lower()
        self.assertNotIn("holds are optional, not a default", text)
        self.assertNotIn("imposing pre/post holds", text)
        for term in ("sudden lunge", "requested end hold", "needle", "neck",
                     "pre-lunge hold", "optional", "conditional repair", "veil"):
            self.assertIn(term, text)

    def test_acting_self_check_distinguishes_source_holds_from_added_repairs(self):
        text = normalized(SKILLS / "seedance-acting-console/SKILL.md")
        checklist = text.split("## self-check checklist", 1)[1]
        self.assertNotIn("use holds only when selected", checklist)
        self.assertIn("preserve source-requested holds", checklist)
        self.assertIn("additional holds", checklist)
        self.assertIn("optional", checklist)
        self.assertIn("demonstrated problem", checklist)
        self.assertIn("source locks", checklist)
        self.assertIn("no burst count is an acceptance condition", checklist)

    def test_compilers_and_reviews_do_not_soften_body_or_cap_bursts(self):
        paths = [
            SKILLS / "seedance-prompt-25/references/scene-action.md",
            SKILLS / "seedance-prompt-20/SKILL.md",
            SKILLS / "seedance-acting-console/SKILL.md",
            SKILLS / "seedance-acting-console/references/restraint-and-shape.md",
            SKILLS / "prompt-review/references/checklist-seedance-25.md",
            SKILLS / "prompt-review/references/checklist-seedance-legacy.md",
        ]
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                self.assertNotIn("prefer slow, gentle", text)
                self.assertNotIn("prefers slow, gentle", text)
                self.assertNotIn("appears at most once per shot", text)
                self.assertNotIn("at most one per shot", text)
                self.assertNotIn("at most one burst action", text)
                self.assertIn("intent", text)
                self.assertRegex(text, r"readability|readable|smearing")
                self.assertIn("recovery", text)

    def test_dialogue_does_not_automatically_prohibit_kinetic_coverage(self):
        paths = [
            SKILLS / "seedance-shot-design/SKILL.md",
            SKILLS / "seedance-shot-design/references/coverage-patterns.md",
            SKILLS / "seedance-shot-design/references/worked-repairs.md",
            SKILLS / "seedance-prompt-25/references/shot-staging.md",
            SKILLS / "prompt-review/references/checklist-seedance-25.md",
        ]
        prohibited = (
            "only for shots without spoken lines",
            "keep their moves quiet",
            "keep moves slow while a line",
            "keep them slow so lips",
            "large moves there are minor",
            "no large move is planned during a spoken line",
            "silhouette is for shots without speech",
            "no silhouette on a shot with spoken lines",
            "a silhouette only on shots without speech",
        )
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                for phrase in prohibited:
                    self.assertNotIn(phrase, text)
                self.assertIn("readability", text)

    def test_entrypoints_and_references_do_not_reintroduce_coverage_quotas(self):
        paths = [
            SKILLS / "ugc-ad-modes/SKILL.md",
            SKILLS / "film-production/SKILL.md",
            SKILLS / "film-production/references/stage-contracts.md",
            SKILLS / "film-production/references/production-defaults.md",
            SKILLS / "seedance-prompt-25/references/shot-staging.md",
            SKILLS / "seedance-shot-design/SKILL.md",
            SKILLS / "brief-intake/SKILL.md",
            SKILLS / "brief-intake/references/worked-repairs.md",
            SKILLS / "prompt-review/references/checklist-seedance-legacy.md",
        ]
        prohibited = (
            "build a 30 s spot from about six",
            "ads and tvcs group shots into sequences of",
            "each sequence has one",
            "one wow image per sequence",
            "each with a camera move, a named light and one wow",
            "and neighboring shots differ",
            "adjacent shots differ in at least two",
            "at least one shot per scene is not plain eye level",
            "does not run on clean singles alone",
            "vary size and angle across a scene",
        )
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                for phrase in prohibited:
                    self.assertNotIn(phrase, text)
                self.assertRegex(text, r"optional|no .*quota|not .*quota")
        rules = json.loads((ROOT / ".agents/contracts/rules.json").read_text())["rules"]
        variety = next(rule for rule in rules if rule["id"] == "shot.variety")
        self.assertNotIn("at least two", variety["summary"])
        self.assertIn("intent", variety["summary"])
        self.assertIn("hold", variety["summary"])
        policy = normalized(ROOT / ".agents/contracts/production-policy.md")
        self.assertNotIn("missing move or light on the shot flagged as the turn", policy)

    def test_creative_intake_resolves_open_premise_without_expanding_scoped_work(self):
        for name in ("brief-intake", "ugc-ad-modes"):
            with self.subTest(skill=name):
                text = normalized(SKILLS / name / "SKILL.md")
                for term in ("premise", "attention", "payoff", "alternatives", "scoped"):
                    self.assertIn(term, text)
                self.assertRegex(text, r"missing|underspecified|vague")
                self.assertRegex(text, r"no .*alternatives|not .*alternatives")

    def test_sound_and_artistic_acceptance_are_carried_before_and_after_generation(self):
        paths = [
            ROOT / "AGENTS.md",
            ROOT / ".agents/contracts/performance-direction.md",
            ROOT / ".agents/contracts/production-policy.md",
            SKILLS / "film-production/references/stage-contracts.md",
            SKILLS / "film-production/references/production-defaults.md",
        ]
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                for term in ("sound", "editorial", "before generation", "artistic",
                             "playback", "timestamps", "brief"):
                    self.assertIn(term, text)
                self.assertRegex(text, r"unavailable|unresolved")

    def test_evaluation_expectations_do_not_reward_blanket_activity(self):
        names = ("brief-intake", "film-production", "seedance-prompt-25", "seedance-prompt-20",
                 "seedance-shot-design", "seedance-acting-console", "ugc-ad-modes")
        for name in names:
            cases = json.loads((SKILLS / name / "evals/evals.json").read_text())["evals"]
            for case in cases:
                with self.subTest(skill=name, case=case["id"]):
                    text = " ".join([case["expected_output"],
                                     *case.get("assertions", case.get("expectations", []))])
                    text = " ".join(text.lower().split())
                    self.assertNotRegex(text, r"(?:plans|proposes) about (?:five or )?six")
                    self.assertNotIn("adjacent shots differ in at least two", text)
                    self.assertNotIn("exactly one burst action", text)
                    self.assertNotIn("one wow image", text)
        fixture = json.loads(
            (ROOT / "tests/fixtures/creative_quality_shot_design_cases.json").read_text()
        )
        for case in fixture["cases"]:
            text = " ".join(case["criteria"].values()).lower()
            self.assertNotIn("at least two", text)
            self.assertNotIn("shot lengths are uneven", text)
            self.assertNotIn("moves stay quiet during spoken lines", text)
            self.assertNotIn("rather than holding one framing", text)
            self.assertNotIn("each short shot has a distinct camera setup", text)
            self.assertNotIn("different key directions for the two speakers", text)
            self.assertNotIn("most emphasized moment", text)
            self.assertNotIn("escalating pursuit", text)

    def test_framing_repairs_do_not_invent_blocking_or_importance(self):
        text = normalized(SKILLS / "seedance-shot-design/references/framing.md")
        self.assertNotIn("stage the height difference", text)
        self.assertNotIn("size says the subject does not matter", text)
        self.assertNotIn("the more a subject matters to the beat, the larger", text)
        self.assertIn("readable", text)

    def test_framing_evals_preserve_source_beats_without_mandatory_recipes(self):
        document = json.loads(
            (SKILLS / "seedance-shot-design/evals/evals.json").read_text()
        )
        cases = {case["id"]: case for case in document["evals"]}
        source_terms = {
            11: ("seated elder", "kneeling young man", "resisting", "takes control"),
            12: ("14-second", "bloodied glove", "locker", "two partners"),
            13: ("four shots", "grandmother", "seated grandson", "stands up"),
        }
        prohibited = (
            "his coverage keeps her in the foreground",
            "the angle changes at the turn",
            "a push-in is given only",
            "in that order",
            "covered by one three-shot rather than three singles",
            "the coverage uses an over-the-hip",
            "an over-the-shoulder replaces it",
            "changes once at the turn",
            "only once rather than every shot",
        )
        for identifier, terms in source_terms.items():
            with self.subTest(case=identifier):
                case = cases[identifier]
                text = " ".join(
                    [case["expected_output"], *case["assertions"]]
                ).lower()
                for phrase in prohibited:
                    self.assertNotIn(phrase, text)
                self.assertIn("optional", text)
                self.assertIn("readable", text)
                for term in terms:
                    self.assertIn(term, text)
        self.assertIn("without dialogue", cases[11]["prompt"])
        self.assertIn("without dialogue", cases[13]["prompt"])

    def test_closing_cadence_is_readability_led_not_a_state_change_quota(self):
        paths = [
            SKILLS / "seedance-shot-design/SKILL.md",
            SKILLS / "seedance-prompt-25/references/shot-staging.md",
            SKILLS / "ugc-ad-modes/SKILL.md",
            SKILLS / "prompt-review/references/checklist-seedance-25.md",
            ROOT / ".agents/contracts/rules.json",
        ]
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                self.assertNotIn("more than two visible state changes", text)
                self.assertNotIn("at most two state changes", text)
                self.assertNotIn("one or two state changes", text)
                self.assertIn("closing beats", text)
                self.assertIn("readability", text)
                self.assertIn("provisional", text)
                self.assertIn("locked", text)

    def test_camera_support_preserves_blocking_and_optional_pov_coverage(self):
        for relative in (
            "seedance-camera-presets/SKILL.md",
            "seedance-shot-design/references/framing.md",
        ):
            with self.subTest(path=relative):
                text = normalized(SKILLS / relative)
                self.assertNotIn("use only when the two characters", text)
                self.assertNotIn("while <lower character>", text)
                self.assertNotIn("keep a pov shot adjacent", text)
                self.assertNotIn("cover it with a shot of the looker", text)
                self.assertNotIn("a hold lands best after motion", text)
                self.assertIn("optional", text)
                self.assertIn("blocking", text)
        cases = json.loads(
            (SKILLS / "seedance-camera-presets/evals/evals.json").read_text()
        )["evals"]
        case = next(case for case in cases if case["id"] == 10)
        text = " ".join([case["expected_output"], *case["expectations"]]).lower()
        self.assertIn("optional", text)
        self.assertNotIn("should sit beside", text)
        self.assertIn("letter", text)
        self.assertIn("ana", text)

    def test_camera_move_counts_are_planning_heuristics_across_consumers(self):
        paths = (
            "seedance-camera-presets/SKILL.md",
            "seedance-shot-design/SKILL.md",
            "seedance-shot-design/references/coverage-patterns.md",
            "seedance-prompt-20/SKILL.md",
            "seedance-prompt-25/references/shot-staging.md",
            "prompt-review/references/checklist-seedance-25.md",
            "prompt-review/references/checklist-seedance-legacy.md",
            "prompt-review/references/checklist-seedance-edits.md",
            "seedance-pacing-presets/SKILL.md",
            "seedance-kinetic-ads/SKILL.md",
            "seedance-music-video/SKILL.md",
            "seedance-music-video/references/music-video-recipes.md",
            "template-factory/references/slot-mapping.md",
        )
        for path in (
            *(SKILLS / relative for relative in paths),
            ROOT / ".agents/contracts/seedance-reference.md",
        ):
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                self.assertNotRegex(
                    text,
                    r"at most (?:one secondary|one compatible secondary|two camera moves|2 per shot)"
                    r"|(?:keep|use) 1[-–]2 camera moves"
                    r"|≤2 moves|2 or fewer simultaneous moves|toward the move limit"
                    r"|camera movement or transition \(one primary move\)"
                    r"|one or two (?:clear requested movements|coherent camera moves)",
                )
                self.assertIn("planning heuristic", text)
                self.assertIn("choreography", text)
                self.assertRegex(text, r"readab(?:le|ility)")
                self.assertRegex(text, r"incompatible|competing|conflict")
        effects = normalized(
            SKILLS / "seedance-effects-studio/references/effects-product-and-spectacle.md"
        )
        self.assertNotIn("two moves, the limit", effects)

    def test_camera_evals_and_quality_rubrics_do_not_reward_move_caps(self):
        for name in ("seedance-camera-presets", "seedance-shot-design", "seedance-music-video"):
            cases = json.loads((SKILLS / name / "evals/evals.json").read_text())["evals"]
            for case in cases:
                with self.subTest(skill=name, case=case["id"]):
                    text = " ".join([
                        case["expected_output"],
                        *case.get("assertions", case.get("expectations", [])),
                    ]).lower()
                    self.assertNotRegex(
                        text,
                        r"at or below 2|at most (?:two|one secondary)"
                        r"|(?:no|neither).{0,35}more than (?:two|one primary)",
                    )
        fixture = json.loads(
            (ROOT / "tests/fixtures/creative_quality_shot_design_cases.json").read_text()
        )
        for case in fixture["cases"]:
            self.assertNotIn("at most one secondary", " ".join(case["criteria"].values()))

    def test_camera_eval_boundaries_cover_choreography_conflicts_and_missing_inputs(self):
        cases = {
            case["id"]: case
            for case in json.loads(
                (SKILLS / "seedance-camera-presets/evals/evals.json").read_text()
            )["evals"]
        }
        for identifier, terms in {
            13: ("three simultaneous", "orbit", "craning", "tilt", "no cuts"),
            14: ("pan left", "pan right", "same time"),
            15: ("three moves", "subject", "start", "end"),
        }.items():
            with self.subTest(case=identifier):
                self.assertIn(identifier, cases)
                case = cases[identifier]
                for term in terms:
                    self.assertIn(term, case["prompt"].lower())
                text = " ".join([case["expected_output"], *case["expectations"]]).lower()
                self.assertIn("count", text)
                self.assertRegex(text, r"readability|readable|unresolved")
        if all(identifier in cases for identifier in (13, 14, 15)):
            self.assertIn("preserve", cases[13]["expected_output"].lower())
            self.assertIn("incompatible", cases[14]["expected_output"].lower())
            self.assertIn("unresolved", cases[15]["expected_output"].lower())

    def test_camera_sanity_preserves_static_locks_and_direction_checks(self):
        text = normalized(SKILLS / "seedance-camera-presets/SKILL.md")
        checklist = text.split("## self-check checklist", 1)[1]
        self.assertIn("incompatible", checklist)
        self.assertIn("readability", checklist)
        self.assertIn("static", checklist)
        self.assertIn("starts and ends", checklist)
        self.assertIn("in order", checklist)
        edits = normalized(SKILLS / "prompt-review/references/checklist-seedance-edits.md")
        self.assertIn("n/a when the edit must preserve the source camera", edits)

    def test_progressive_change_does_not_require_slowing_readable_action(self):
        paths = (
            "seedance-pacing-presets/SKILL.md",
            "seedance-prompt-25/references/scene-action.md",
            "prompt-review/references/checklist-seedance-25.md",
        )
        for relative in paths:
            with self.subTest(path=relative):
                text = normalized(SKILLS / relative)
                self.assertNotIn("slow the movement so the crossing", text)
                self.assertNotIn("slow enough that the crossing", text)
                self.assertIn("optional repair", text)
                self.assertIn("demonstrated", text)
                self.assertIn("source", text)
        cases = json.loads(
            (SKILLS / "seedance-pacing-presets/evals/evals.json").read_text()
        )["evals"]
        case = next(case for case in cases if case["id"] == 9)
        text = " ".join([case["expected_output"], *case["expectations"]]).lower()
        self.assertNotIn("is slowed so", text)
        self.assertIn("optional", text)
        self.assertIn("unbroken", text)
        self.assertIn("post", text)

    def test_motion_flags_distinguish_creative_advice_from_provider_constraints(self):
        text = normalized(SKILLS / "ugc-motion-presets/SKILL.md")
        self.assertNotIn("flags encode real provider constraints", text)
        self.assertIn("creative", text)
        self.assertIn("provider", text)
        self.assertIn("optional", text)
        text = normalized(
            SKILLS / "ugc-motion-presets/references/execution-constraints.md"
        )
        self.assertNotIn("moderate dynamics", text)
        self.assertIn("optional repair", text)
        self.assertIn("demonstrated", text)
        self.assertIn("intent", text)

    def test_short_cut_guidance_is_provisional_and_preserves_requested_rhythm(self):
        paths = (
            "seedance-pacing-presets/SKILL.md",
            "seedance-pacing-presets/references/assembly-cuts.md",
            "seedance-pacing-presets/references/cut-transitions.md",
            "seedance-shot-design/SKILL.md",
            "seedance-shot-design/references/coverage-patterns.md",
            "prompt-review/references/checklist-seedance-25.md",
            "prompt-review/references/author-self-check.md",
            "seedance-prompt-25/SKILL.md",
            "seedance-prompt-25/references/shot-staging.md",
            "film-production/references/production-defaults.md",
            "film-production/references/stage-contracts.md",
            "ugc-ad-modes/SKILL.md",
            "seedance-vfx-prompt/SKILL.md",
            "seedance-motion-design/SKILL.md",
            "seedance-animation-styles/SKILL.md",
            "template-factory/references/long-pins-and-multi-clip.md",
        )
        prohibited = (
            "shots shorter than about 0.8 s are merged or dropped",
            "shots shorter than about 0.8 s merge",
            "about 0.8 s is merged or dropped",
            "no shot inside one clip is shorter",
            "at most about 7 shots",
            "none shorter than about 0.8 s",
            "respect the shot ceiling",
            "the shot ceiling in step 4",
            "hard cuts leave at least about 0.8 s",
            "never requested inside one prompt",
            "a single prompt cannot make the picture skip",
            "never ask a single prompt for these cuts",
            "shots under about 0.8 s merge",
            "keep every planned shot at least about 0.8 s",
            "shot count and lengths fit the duration and the shot ceiling",
            "no in-clip shot is shorter",
            "assembly-only cuts",
        )
        for path in (
            *(SKILLS / relative for relative in paths),
            ROOT / ".agents/contracts/seedance-reference.md",
        ):
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path)
                for phrase in prohibited:
                    self.assertNotIn(phrase, text)
                for term in ("provisional", "heuristic", "provider", "rhythm", "assembly"):
                    self.assertIn(term, text)
                self.assertRegex(text, r"preserve|preserving")
                self.assertRegex(text, r"precision|precise|frame-accurate")
                self.assertRegex(text, r"omit|omission|skipped action")
                self.assertIn("conflict", text)

    def test_short_cut_evals_do_not_reward_automatic_retiming_or_rejection(self):
        prohibited = (
            "within the shot ceiling",
            "at most about 7 shots",
            "none shorter than about 0.8 s",
            "shots under about 0.8 s merge",
            "are merged or dropped inside one clip",
            "in-prompt cut list has fewer shots",
            "cut is too short for one clip",
            "assembly-only",
        )
        for name in (
            "seedance-pacing-presets", "seedance-shot-design", "seedance-prompt-25",
            "film-production", "seedance-music-video", "ugc-ad-modes",
            "seedance-motion-design", "seedance-animation-styles", "template-factory",
        ):
            cases = json.loads((SKILLS / name / "evals/evals.json").read_text())["evals"]
            for case in cases:
                with self.subTest(skill=name, case=case["id"]):
                    text = " ".join([
                        case["expected_output"],
                        *case.get("assertions", case.get("expectations", [])),
                    ]).lower()
                    for phrase in prohibited:
                        self.assertNotIn(phrase, text)
                    self.assertNotIn("no shot inside the clip is shorter than about 0.8 s", text)
                    self.assertNotIn("shots of at least about 0.8 s", text)

    def test_short_cut_evals_cover_preservation_conflicts_and_missing_timing(self):
        cases = {
            case["id"]: case
            for case in json.loads(
                (SKILLS / "seedance-pacing-presets/evals/evals.json").read_text()
            )["evals"]
        }
        boundaries = {
            11: ("eight", "0.5", "preserve", "provisional"),
            12: ("six", "0.8", "conflict", "locked"),
            13: ("0.3", "frame rate", "missing", "omit"),
        }
        for identifier, terms in boundaries.items():
            with self.subTest(case=identifier):
                self.assertIn(identifier, cases)
                case = cases[identifier]
                text = " ".join([
                    case["prompt"], case["expected_output"], *case["expectations"]
                ]).lower()
                for term in terms:
                    self.assertIn(term, text)
                self.assertIn("no generation", case["prompt"].lower())
        for identifier in (11, 13):
            if identifier in cases:
                self.assertIn("assembly", cases[identifier]["expected_output"].lower())

    def test_new_cases_cover_quiet_energetic_missing_and_scoped_boundaries(self):
        path = ROOT / "tests/fixtures/creative_quality_defaults_cases.json"
        self.assertTrue(path.is_file())
        document = json.loads(path.read_text())
        cases = {case["id"]: case for case in document["cases"]}
        expected = {
            "quiet_polished_hold", "energetic_dialogue", "legacy_repeated_bursts",
            "missing_premise", "scoped_hook", "sound_led_reveal",
            "unavailable_playback", "localized_variant_locks",
        }
        self.assertEqual(set(cases), expected)
        self.assertEqual(len(cases), len(document["cases"]))
        for case in cases.values():
            self.assertTrue(case["prompt"].strip())
            self.assertGreaterEqual(len(case["criteria"]), 3)
            self.assertTrue(all(value.strip() for value in case["criteria"].values()))
            self.assertIn("preservation", case["criteria"])
        self.assertIn("no generation", normalized(path))
        self.assertTrue(re.search(r"unverified|unresolved", normalized(path)))


if __name__ == "__main__":
    unittest.main()

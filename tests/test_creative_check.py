from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/ad-creative-check/scripts/creative_check.py"
SPEC = importlib.util.spec_from_file_location("creative_check", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

FFMPEG_AVAILABLE = bool(shutil.which("ffmpeg"))
DELIVERABLE = "glow-serum_hook-question_9x16_15s_v01_meta-instagram-reels"
FRAME = "frames/frame_00002.png"
CAMPAIGN = "glow-serum"
VIDEO = "glow-serum-9x16/studio/renders/cut.mp4"
VIDEO_BYTES = b"synthetic cut bytes"
VIDEO_SHA256 = hashlib.sha256(VIDEO_BYTES).hexdigest()
RECORD = f"delivery/disclosure_{DELIVERABLE}.json"


def passing_checks() -> list[dict[str, Any]]:
    visual = {"timestamps": [1.0], "frames": [FRAME]}
    return [
        {"id": "product_reveal", "status": "pass", "evidence": "Bottle in hand.", **visual},
        {"id": "logo_legible", "status": "pass", "evidence": "End card logo matches kit.", **visual},
        {"id": "opening_change", "status": "pass", "evidence": "Cut at 1 s.", **visual},
        {"id": "cta_safe_zone", "status": "pass", "evidence": "CTA inside zone.", **visual},
        {"id": "sound_off_readable", "status": "pass", "evidence": "Offer on screen 2 s.", **visual},
        {"id": "claims_supported", "status": "pass", "evidence": "One claim, fact f-01 supported.", "timestamps": [4.0]},
        {"id": "brand_copy", "status": "pass", "evidence": "No banned words; required line present."},
        {"id": "speech_intelligible", "status": "pass", "evidence": "Transcript matches the script."},
        {
            "id": "loudness_target",
            "status": "pass",
            "evidence": "loudnorm measurement",
            "measured": {"integrated_lufs": -16.4, "true_peak_dbtp": -1.8},
        },
        {
            "id": "disclosure_recorded",
            "status": "pass",
            "evidence": "User chose end-card disclosure.",
            "disclosure_record": RECORD,
        },
    ]


def checklist(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema_version": 1,
        "deliverable_id": DELIVERABLE,
        "video": VIDEO,
        "video_sha256": VIDEO_SHA256,
        "duration_s": 15.0,
        "paid": True,
        "placement": "meta-instagram-reels",
        "checks": passing_checks(),
    }
    document.update(overrides)
    return document


def decision(**overrides: Any) -> dict[str, Any]:
    record = {
        "schema_version": 1,
        "deliverable_id": DELIVERABLE,
        "paid": True,
        "decision": "disclose",
        "decided_by": "user",
        "user_quote": "Yes, disclose on the end card.",
    }
    record.update(overrides)
    return record


def replace_check(document: dict[str, Any], check_id: str, **fields: Any) -> dict[str, Any]:
    updated = copy.deepcopy(document)
    for check in updated["checks"]:
        if check["id"] == check_id:
            check.update(fields)
    return updated


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="creative-check-test-")
        self.addCleanup(self.directory.cleanup)
        self.projects = Path(self.directory.name)
        self.project = self.projects / CAMPAIGN
        self.root = self.project / "delivery" / "qa" / DELIVERABLE
        (self.root / "frames").mkdir(parents=True)
        (self.root / FRAME).write_bytes(b"\x89PNG\r\n\x1a\n")
        self.record = self.project / RECORD
        self.record.write_text(json.dumps(decision()))
        self.video = self.projects / VIDEO
        self.video.parent.mkdir(parents=True)
        self.video.write_bytes(VIDEO_BYTES)

    def run_report(self, document: Any) -> tuple[int, dict[str, Any]]:
        path = self.root / "checks.json"
        path.write_text(json.dumps(document))
        return MODULE.report(path, self.project)

    def assert_invalid(self, document: Any, fragment: str) -> None:
        code, result = self.run_report(document)
        self.assertEqual(code, 2)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any(fragment in error for error in result["errors"]),
            f"{fragment!r} not in {result['errors']}",
        )

    def test_all_passing_checks_give_pass_verdict_with_rule_ids(self) -> None:
        code, result = self.run_report(checklist())
        self.assertEqual(code, 0)
        self.assertTrue(result["valid"])
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["counts"]["pass"], 10)
        rules = {check["id"]: check["rule_id"] for check in result["checks"]}
        self.assertEqual(rules["claims_supported"], "ad.claims_supported")
        self.assertEqual(rules["cta_safe_zone"], "ad.safe_zone")
        self.assertEqual(rules["disclosure_recorded"], "ad.disclosure_recorded")
        self.assertEqual(rules["brand_copy"], "brand.copy_rules")
        self.assertNotIn("score", json.dumps(result))

    def test_one_failure_makes_the_verdict_fail(self) -> None:
        document = replace_check(checklist(), "logo_legible", status="fail", evidence="Logo stretched.")
        code, result = self.run_report(document)
        self.assertEqual(code, 1)
        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(result["counts"]["fail"], 1)

    def test_needs_human_without_failure_gives_needs_human_verdict(self) -> None:
        document = replace_check(checklist(), "cta_safe_zone", status="needs_human", evidence="Safe zone unpublished.")
        code, result = self.run_report(document)
        self.assertEqual(code, 1)
        self.assertEqual(result["verdict"], "needs_human")

    def test_missing_check_is_invalid(self) -> None:
        document = checklist()
        document["checks"] = [check for check in document["checks"] if check["id"] != "brand_copy"]
        self.assert_invalid(document, "brand_copy: missing check")

    def test_duplicate_check_is_invalid(self) -> None:
        document = checklist()
        document["checks"].append(copy.deepcopy(document["checks"][0]))
        self.assert_invalid(document, "product_reveal: listed more than once")

    def test_schema_rejects_unknown_status_and_extra_keys(self) -> None:
        self.assert_invalid(replace_check(checklist(), "brand_copy", status="maybe"), "status")
        self.assert_invalid(checklist(virality_score=9), "virality_score")
        self.assert_invalid(checklist(video_sha256="xyz"), "video_sha256")

    def test_reveal_after_declared_time_cannot_pass(self) -> None:
        late = replace_check(checklist(), "product_reveal", timestamps=[3.1])
        self.assert_invalid(late, "product_reveal: pass needs evidence at or before 2.0 s")
        code, _ = self.run_report(dict(late, reveal_time_s=4.0))
        self.assertEqual(code, 0)

    def test_late_opening_change_cannot_pass(self) -> None:
        document = replace_check(checklist(), "opening_change", timestamps=[2.5])
        self.assert_invalid(document, "opening_change: pass needs evidence at or before 2.0 s")

    def test_visual_pass_needs_frames_and_timestamps(self) -> None:
        document = replace_check(checklist(), "logo_legible", frames=[], timestamps=[])
        self.assert_invalid(document, "logo_legible: pass needs timestamps")
        self.assert_invalid(document, "logo_legible: pass needs frame paths")

    def test_frame_paths_are_confined_and_must_exist(self) -> None:
        self.assert_invalid(replace_check(checklist(), "product_reveal", frames=["../outside.png"]), "must stay inside")
        self.assert_invalid(replace_check(checklist(), "product_reveal", frames=["frames/missing.png"]), "frame not found")

    def test_timestamp_beyond_cut_is_invalid(self) -> None:
        document = replace_check(checklist(), "claims_supported", timestamps=[16.0])
        self.assert_invalid(document, "after the 15.0 s cut")

    def test_not_applicable_is_refused_for_core_checks(self) -> None:
        document = replace_check(checklist(), "product_reveal", status="not_applicable", frames=[], timestamps=[])
        self.assert_invalid(document, "product_reveal: not_applicable is not allowed")

    def test_loudness_status_must_agree_with_measurement(self) -> None:
        loud = replace_check(checklist(), "loudness_target", measured={"integrated_lufs": -11.0, "true_peak_dbtp": -1.0})
        self.assert_invalid(loud, "measured values say fail, recorded pass")
        hot_peak = replace_check(checklist(), "loudness_target", measured={"integrated_lufs": -16.0, "true_peak_dbtp": -0.5})
        self.assert_invalid(hot_peak, "measured values say fail")
        unmeasured = copy.deepcopy(checklist())
        unmeasured["checks"][8].pop("measured")
        self.assert_invalid(unmeasured, "loudness_target: pass needs measured values")

    def test_custom_loudness_target_is_used(self) -> None:
        document = replace_check(checklist(), "loudness_target", measured={"integrated_lufs": -14.2, "true_peak_dbtp": -1.2})
        document["loudness_target"] = {"integrated_lufs": -14.0, "true_peak_dbtp": -1.0, "tolerance_lu": 0.5}
        code, _ = self.run_report(document)
        self.assertEqual(code, 0)

    def test_unpaid_deliverable_records_disclosure_not_applicable(self) -> None:
        internal = replace_check(
            checklist(paid=False),
            "disclosure_recorded",
            status="not_applicable",
            evidence="Internal showreel, label-free.",
        )
        code, result = self.run_report(internal)
        self.assertEqual(code, 0)
        self.assertEqual(result["counts"]["not_applicable"], 1)
        self.assert_invalid(checklist(paid=False), "unpaid deliverables stay label-free")

    def test_paid_deliverable_cannot_skip_disclosure(self) -> None:
        document = replace_check(checklist(), "disclosure_recorded", status="not_applicable")
        self.assert_invalid(document, "a paid deliverable needs a recorded disclosure decision")
        failing = replace_check(checklist(), "disclosure_recorded", status="fail", evidence="No decision yet.")
        code, result = self.run_report(failing)
        self.assertEqual((code, result["verdict"]), (1, "fail"))

    def test_disclosure_record_must_be_the_users_decision_for_this_deliverable(self) -> None:
        self.record.write_text(json.dumps(decision(decided_by="agent")))
        self.assert_invalid(checklist(), "decision must be the user's")
        self.record.write_text(json.dumps(decision(deliverable_id="other-ad_v01")))
        self.assert_invalid(checklist(), "record is for another deliverable")
        self.record.write_text(json.dumps(decision(decision="maybe")))
        self.assert_invalid(checklist(), "decision must be disclose")
        self.record.unlink()
        self.assert_invalid(checklist(), "record not found")

    def test_disclosure_record_is_read_from_the_campaign_delivery_folder_only(self) -> None:
        (self.root / "disclosure.json").write_text(json.dumps(decision()))
        in_check_folder = replace_check(checklist(), "disclosure_recorded", disclosure_record="disclosure.json")
        self.assert_invalid(in_check_folder, f"disclosure_record must be {RECORD}")
        escaping = replace_check(checklist(), "disclosure_recorded", disclosure_record="../outside.json")
        self.assert_invalid(escaping, f"disclosure_record must be {RECORD}")

    def test_symlinked_disclosure_record_is_refused(self) -> None:
        target = self.projects / "elsewhere.json"
        target.write_text(json.dumps(decision()))
        self.record.unlink()
        self.record.symlink_to(target)
        self.assert_invalid(checklist(), "regular file")

    def test_video_must_exist(self) -> None:
        self.video.unlink()
        self.assert_invalid(checklist(), "video not found")

    def test_video_hash_must_match_the_file(self) -> None:
        self.assert_invalid(checklist(video_sha256="0" * 64), "video_sha256 does not match")

    def test_video_in_the_campaign_project_itself_is_accepted(self) -> None:
        local = self.project / "studio/renders/cut.mp4"
        local.parent.mkdir(parents=True)
        local.write_bytes(VIDEO_BYTES)
        code, result = self.run_report(checklist(video=f"{CAMPAIGN}/studio/renders/cut.mp4"))
        self.assertEqual(code, 0, result)

    def test_video_outside_the_campaign_projects_is_refused(self) -> None:
        other = self.projects / "other-brand/studio/renders/cut.mp4"
        other.parent.mkdir(parents=True)
        other.write_bytes(VIDEO_BYTES)
        for video in ("other-brand/studio/renders/cut.mp4", "../cut.mp4", "/tmp/cut.mp4", "glow-serumx/cut.mp4"):
            self.assert_invalid(checklist(video=video), "video must")

    def test_symlinked_video_is_refused(self) -> None:
        link = self.project / "studio/renders/link.mp4"
        link.parent.mkdir(parents=True)
        link.symlink_to(self.video)
        self.assert_invalid(checklist(video=f"{CAMPAIGN}/studio/renders/link.mp4"), "regular file")

    def test_checklist_must_sit_in_its_deliverable_qa_folder(self) -> None:
        stray = self.project / "delivery/qa/another-deliverable"
        (stray / "frames").mkdir(parents=True)
        (stray / FRAME).write_bytes(b"png")
        path = stray / "checks.json"
        path.write_text(json.dumps(checklist()))
        code, result = MODULE.report(path, self.project)
        self.assertEqual(code, 2)
        self.assertTrue(any("delivery/qa/" in error for error in result["errors"]), result)

    def test_missing_project_folder_is_invalid(self) -> None:
        path = self.root / "checks.json"
        path.write_text(json.dumps(checklist()))
        code, result = MODULE.report(path, self.projects / "absent")
        self.assertEqual(code, 2)
        self.assertIn("project", result["errors"][0])

    def test_unreadable_checklist_is_invalid(self) -> None:
        path = self.root / "checks.json"
        path.write_text("{not json")
        code, result = MODULE.report(path, self.project)
        self.assertEqual(code, 2)
        self.assertIn("cannot read", result["errors"][0])

    def test_cli_report_writes_summary_only_when_valid(self) -> None:
        path = self.root / "checks.json"
        path.write_text(json.dumps(checklist()))
        out = self.root / "report.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = MODULE.main(["report", str(path), "--project", str(self.project), "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.read_text())["verdict"], "pass")
        out.unlink()
        path.write_text(json.dumps(checklist(schema_version=2)))
        with contextlib.redirect_stdout(io.StringIO()):
            code = MODULE.main(["report", str(path), "--project", str(self.project), "--out", str(out)])
        self.assertEqual(code, 2)
        self.assertFalse(out.exists())

    def test_cli_report_refuses_an_out_path_outside_the_check_folder(self) -> None:
        path = self.root / "checks.json"
        path.write_text(json.dumps(checklist()))
        out = self.project / "report.json"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = MODULE.main(["report", str(path), "--project", str(self.project), "--out", str(out)])
        self.assertEqual(code, 2)
        self.assertFalse(out.exists())

    def test_cli_report_requires_the_project(self) -> None:
        path = self.root / "checks.json"
        path.write_text(json.dumps(checklist()))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            MODULE.main(["report", str(path)])
        self.assertEqual(raised.exception.code, 2)


class FrameCommandTests(unittest.TestCase):
    def test_command_is_an_argument_array_with_rate_from_interval(self) -> None:
        command = MODULE.frame_command(Path("cut file.mp4"), Path("qa/frames"), 0.5)
        self.assertEqual(command[0], "ffmpeg")
        self.assertIn("cut file.mp4", command)
        self.assertEqual(command[command.index("-vf") + 1], "fps=2/1")
        self.assertEqual(command[-1], str(Path("qa/frames") / "frame_%05d.png"))
        self.assertNotIn("-t", command)

    def test_fractional_intervals_and_until(self) -> None:
        command = MODULE.frame_command(Path("cut.mp4"), Path("out"), 0.3, until=3)
        self.assertEqual(command[command.index("-vf") + 1], "fps=10/3")
        self.assertEqual(command[command.index("-t") + 1], "3")
        two_seconds = MODULE.frame_command(Path("cut.mp4"), Path("out"), 2.0)
        self.assertEqual(two_seconds[two_seconds.index("-vf") + 1], "fps=1/2")

    def test_invalid_intervals_are_rejected(self) -> None:
        for every in (0, -1, 10.5):
            with self.assertRaises(ValueError):
                MODULE.frame_command(Path("cut.mp4"), Path("out"), every)
        with self.assertRaises(ValueError):
            MODULE.frame_command(Path("cut.mp4"), Path("out"), 0.5, until=0)

    def test_missing_video_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            MODULE.sample_frames(Path(directory) / "absent.mp4", Path(directory) / "frames", 0.5, None)


@unittest.skipUnless(FFMPEG_AVAILABLE, "ffmpeg is required for frame sampling tests")
class FrameSamplingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="creative-frames-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.video = self.root / "cut.mp4"
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "lavfi",
                "-i", "testsrc=size=160x284:rate=10:duration=2",
                "-pix_fmt", "yuv420p", str(self.video),
            ],
            check=True,
        )

    def test_samples_frames_with_times(self) -> None:
        result = MODULE.sample_frames(self.video, self.root / "frames", 0.5, None)
        times = [frame["time_s"] for frame in result["frames"]]
        self.assertEqual(times[:4], [0.0, 0.5, 1.0, 1.5])
        self.assertIn(len(times), (4, 5))
        self.assertEqual(result["frames"][0]["path"], "frames/frame_00000.png")
        self.assertTrue((self.root / result["frames"][0]["path"]).is_file())
        self.assertEqual(len(result["video_sha256"]), 64)

    def test_until_limits_the_window(self) -> None:
        result = MODULE.sample_frames(self.video, self.root / "opening", 0.25, 1.0)
        self.assertLessEqual(max(frame["time_s"] for frame in result["frames"]), 1.0)

    def test_refuses_a_folder_with_existing_frames(self) -> None:
        MODULE.sample_frames(self.video, self.root / "frames", 1.0, None)
        with self.assertRaises(ValueError):
            MODULE.sample_frames(self.video, self.root / "frames", 1.0, None)


if __name__ == "__main__":
    unittest.main()

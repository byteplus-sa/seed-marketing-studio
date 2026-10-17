from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/brand-kit/scripts/brand_kit.py"
SPEC = importlib.util.spec_from_file_location("brand_kit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

LOGO_BYTES = b"<svg xmlns='http://www.w3.org/2000/svg'><rect width='4' height='4'/></svg>"
FONT_BYTES = b"wOF2-synthetic-font-bytes"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(*argv: str) -> tuple[int, dict[str, Any]]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = MODULE.main(list(argv))
    return code, json.loads(buffer.getvalue())


class BrandKitTestCase(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="brand-kit-test-")
        self.addCleanup(directory.cleanup)
        self.library = Path(directory.name) / "library" / "brands"

    def approved_kit(self) -> Path:
        code, _ = run("init", str(self.library), "acme-home", "--name", "Acme Home")
        self.assertEqual(code, 0)
        kit_dir = self.library / "acme-home"
        (kit_dir / "assets/fonts").mkdir(parents=True)
        (kit_dir / "assets/logo_primary.svg").write_bytes(LOGO_BYTES)
        (kit_dir / "assets/fonts/acmesans-bold.woff2").write_bytes(FONT_BYTES)
        kit = json.loads((kit_dir / "brand.json").read_text())
        kit.update(
            {
                "source": {
                    "method": "website",
                    "urls": ["https://acme-home.example/"],
                    "retrieved_at": "2026-10-17T09:00:00Z",
                    "authorized_by": "User states they are the brand's agency of record",
                },
                "logos": [
                    {
                        "role": "primary",
                        "file": "assets/logo_primary.svg",
                        "sha256": digest(LOGO_BYTES),
                        "source": "https://acme-home.example/press",
                        "min_height_px": 48,
                        "clear_space_ratio": 0.25,
                        "allowed_backgrounds": ["light"],
                    }
                ],
                "palette": [
                    {"name": "acme-red", "hex": "#D7261E", "role": "primary"},
                    {"name": "paper", "hex": "#fafafa", "role": "background"},
                ],
                "typography": [
                    {
                        "role": "headline",
                        "family": "Acme Sans",
                        "weight": 700,
                        "file": "assets/fonts/acmesans-bold.woff2",
                        "sha256": digest(FONT_BYTES),
                        "source": "user_supplied",
                        "license": "Brand-supplied for agency advertising use",
                    }
                ],
                "voice": {"tone": ["warm"], "reading_level": "plain", "do": [], "dont": []},
                "copy_rules": {
                    "banned_words": ["cheap"],
                    "required_lines": [{"text": "Terms apply.", "when": "offer shown"}],
                    "trademark_marks": {"Acme Kettle": "®"},
                },
                "cta_style": {"shape": "pill", "case": "sentence", "verbs": ["Shop now"]},
                "imagery": {"style_sentence": "Soft window light on pale wood surfaces.", "avoid": []},
                "disclosure": {"ai_label_text": None, "placement": None},
                "missing": ["disclosure.ai_label_text", "disclosure.placement"],
                "status": "approved",
                "approval": {
                    "mode": "approve_for_me",
                    "actor": "agent",
                    "decision_ref": "decisions/approve_v01.md",
                    "decided_at": "2026-10-17T10:00:00Z",
                },
            }
        )
        return self.write(kit)

    def write(self, kit: dict[str, Any], path: Path | None = None) -> Path:
        target = path or self.library / "acme-home" / "brand.json"
        target.write_text(json.dumps(kit, indent=2))
        return target

    def edit(self, path: Path, **changes: Any) -> dict[str, Any]:
        kit = json.loads(path.read_text())
        kit.update(changes)
        self.write(kit, path)
        return kit

    def rules(self, path: Path) -> list[str]:
        code, result = run("validate", str(path))
        self.assertEqual(code, int(not result["ok"]))
        return [finding["rule_id"] for finding in result["findings"] if finding["severity"] == "error"]


class InitTests(BrandKitTestCase):
    def test_scaffold_is_a_valid_draft_with_every_unknown_listed(self) -> None:
        code, result = run("init", str(self.library), "acme-home")
        self.assertEqual(code, 0)
        kit_path = Path(result["kit"])
        self.assertTrue((kit_path.parent / "assets").is_dir())
        kit = json.loads(kit_path.read_text())
        self.assertEqual(kit["status"], "draft")
        self.assertIn("name", kit["missing"])
        self.assertIn("logos", kit["missing"])
        self.assertEqual(self.rules(kit_path), [])

    def test_init_refuses_existing_kit(self) -> None:
        run("init", str(self.library), "acme-home")
        code, result = run("init", str(self.library), "acme-home")
        self.assertEqual(code, 1)
        self.assertIn("already exists", result["error"])

    def test_init_rejects_traversal_and_uppercase_ids(self) -> None:
        for brand_id in ("../escape", "Acme", "acme_home", ""):
            with self.subTest(brand_id=brand_id):
                code, result = run("init", str(self.library), brand_id)
                self.assertEqual(code, 1)
                self.assertIn("Invalid brand id", result["error"])
        self.assertFalse((self.library.parent / "escape").exists())


class ValidateTests(BrandKitTestCase):
    def test_complete_approved_kit_passes(self) -> None:
        self.assertEqual(self.rules(self.approved_kit()), [])

    def test_missing_logo_hash_is_rejected(self) -> None:
        path = self.approved_kit()
        kit = json.loads(path.read_text())
        del kit["logos"][0]["sha256"]
        self.write(kit, path)
        self.assertIn("brand.schema", self.rules(path))

    def test_logo_bytes_changed_after_recording_fail_hash_check(self) -> None:
        path = self.approved_kit()
        (path.parent / "assets/logo_primary.svg").write_bytes(LOGO_BYTES + b" ")
        self.assertIn("brand.file_hash", self.rules(path))

    def test_missing_logo_file_is_reported(self) -> None:
        path = self.approved_kit()
        (path.parent / "assets/logo_primary.svg").unlink()
        self.assertIn("brand.file_exists", self.rules(path))

    def test_asset_path_cannot_escape_the_kit(self) -> None:
        path = self.approved_kit()
        kit = json.loads(path.read_text())
        kit["logos"][0]["file"] = "assets/../../outside.svg"
        self.write(kit, path)
        rules = self.rules(path)
        self.assertIn("brand.schema", rules)
        self.assertIn("brand.file_contained", rules)

    def test_symlinked_asset_outside_the_kit_is_rejected(self) -> None:
        path = self.approved_kit()
        outside = self.library.parent / "outside.svg"
        outside.write_bytes(LOGO_BYTES)
        logo = path.parent / "assets/logo_primary.svg"
        logo.unlink()
        logo.symlink_to(outside)
        self.assertIn("brand.file_contained", self.rules(path))

    def test_bad_hex_values_are_flagged(self) -> None:
        path = self.approved_kit()
        for bad in ("D7261E", "#D7261", "#GG261E", "#D7261E00"):
            with self.subTest(hex=bad):
                kit = json.loads(path.read_text())
                kit["palette"][0]["hex"] = bad
                self.write(kit, path)
                self.assertIn("brand.hex", self.rules(path))

    def test_stored_font_without_license_is_an_error_even_in_draft(self) -> None:
        path = self.approved_kit()
        kit = json.loads(path.read_text())
        kit["typography"][0]["license"] = None
        kit["missing"].append("typography.0.license")
        kit["status"] = "draft"
        kit["approval"] = None
        self.write(kit, path)
        self.assertIn("brand.font_license", self.rules(path))

    def test_family_only_font_without_license_warns_in_draft_and_fails_when_approved(self) -> None:
        path = self.approved_kit()
        kit = json.loads(path.read_text())
        kit["typography"][0].update({"file": None, "sha256": None, "license": None, "source": None})
        kit["missing"].extend(
            ["typography.0.file", "typography.0.sha256", "typography.0.license", "typography.0.source"]
        )
        self.write(kit, path)
        self.assertIn("brand.font_license", self.rules(path))
        kit.update({"status": "draft", "approval": None})
        self.write(kit, path)
        code, result = run("validate", str(path))
        self.assertEqual(code, 0)
        self.assertIn(
            ("brand.font_license", "warning"),
            [(finding["rule_id"], finding["severity"]) for finding in result["findings"]],
        )

    def test_unlisted_null_value_is_an_invention_risk(self) -> None:
        path = self.approved_kit()
        self.edit(path, missing=[])
        self.assertIn("brand.missing_listed", self.rules(path))

    def test_approved_kit_needs_an_approval_record(self) -> None:
        path = self.approved_kit()
        self.edit(path, approval=None)
        self.assertIn("brand.schema", self.rules(path))

    def test_brand_id_must_match_directory(self) -> None:
        path = self.approved_kit()
        self.edit(path, brand_id="other-brand")
        self.assertIn("brand.id_matches_directory", self.rules(path))

    def test_validating_from_inside_the_kit_directory_matches_the_brand_id(self) -> None:
        path = self.approved_kit()
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(path.parent)
        self.assertEqual(self.rules(Path("brand.json")), [])
        code, result = run("pin", "brand.json")
        self.assertEqual(code, 0)
        self.assertEqual(result["brand_id"], "acme-home")

    def test_duplicate_palette_names_and_primary_logos_are_rejected(self) -> None:
        path = self.approved_kit()
        kit = json.loads(path.read_text())
        kit["palette"].append({"name": "acme-red", "hex": "#000000", "role": "text"})
        kit["logos"].append(dict(kit["logos"][0]))
        self.write(kit, path)
        rules = self.rules(path)
        self.assertIn("brand.palette_unique", rules)
        self.assertIn("brand.logo_primary", rules)

    def test_invalid_json_and_missing_file_exit_one(self) -> None:
        path = self.approved_kit()
        path.write_text("{not json")
        code, result = run("validate", str(path))
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", result["error"])
        code, result = run("validate", str(path.parent / "absent.json"))
        self.assertEqual(code, 1)

    def test_non_object_kit_reports_schema_error(self) -> None:
        path = self.approved_kit()
        path.write_text("[]")
        self.assertEqual(self.rules(path), ["brand.schema"])

    def test_wrong_shapes_do_not_crash_validation(self) -> None:
        path = self.approved_kit()
        self.edit(path, logos={"role": "primary"}, missing="name", palette=[1, 2])
        self.assertIn("brand.schema", self.rules(path))


class PinAndShowTests(BrandKitTestCase):
    def test_pin_is_stable_across_formatting_and_changes_with_content(self) -> None:
        path = self.approved_kit()
        _, first = run("pin", str(path))
        kit = json.loads(path.read_text())
        path.write_text(json.dumps(kit, separators=(",", ":")))
        _, reformatted = run("pin", str(path))
        self.assertEqual(first["sha256"], reformatted["sha256"])
        kit["palette"][0]["hex"] = "#D7261F"
        self.write(kit, path)
        _, changed = run("pin", str(path))
        self.assertNotEqual(first["sha256"], changed["sha256"])

    def test_pin_expect_detects_mismatch(self) -> None:
        path = self.approved_kit()
        _, pinned = run("pin", str(path))
        code, _ = run("pin", str(path), "--expect", pinned["sha256"])
        self.assertEqual(code, 0)
        code, result = run("pin", str(path), "--expect", "0" * 64)
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])

    def test_pin_refuses_draft_unless_allowed_and_refuses_invalid(self) -> None:
        code, result = run("init", str(self.library), "acme-home")
        draft = Path(result["kit"])
        code, _ = run("pin", str(draft))
        self.assertEqual(code, 1)
        code, result = run("pin", str(draft), "--allow-draft")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "draft")
        self.edit(draft, missing=[])
        code, result = run("pin", str(draft), "--allow-draft")
        self.assertEqual(code, 1)
        self.assertIn("findings", result)

    def test_show_prints_consumer_view(self) -> None:
        path = self.approved_kit()
        code, result = run("show", str(path))
        self.assertEqual(code, 0)
        self.assertEqual(result["palette"], {"acme-red": "#D7261E", "paper": "#fafafa"})
        self.assertEqual(result["banned_words"], ["cheap"])
        self.assertEqual(result["style_sentence"], "Soft window light on pale wood surfaces.")
        _, pinned = run("pin", str(path))
        self.assertEqual(result["pin_sha256"], pinned["sha256"])

    def test_show_refuses_invalid_kit(self) -> None:
        path = self.approved_kit()
        (path.parent / "assets/logo_primary.svg").unlink()
        code, result = run("show", str(path))
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()

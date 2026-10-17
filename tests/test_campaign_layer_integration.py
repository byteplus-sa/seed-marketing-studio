from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)
PAGE = "https://lumo.example/products/travel-mug"


def load(name: str, relative: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BRAND_KIT = load(
    "integration_brand_kit", ".agents/skills/brand-kit/scripts/brand_kit.py"
)
PRODUCT_FACTS = load(
    "integration_product_facts",
    ".agents/skills/product-intake/scripts/product_facts.py",
)
STATIC_BATCH = load(
    "integration_static_batch", ".agents/skills/static-ad-batch/scripts/static_batch.py"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fact(
    fact_id: str, claim: str, status: str, kind: str = "feature"
) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "kind": kind,
        "claim": claim,
        "quote": claim,
        "source_url": PAGE,
        "retrieved_at": "2026-10-17T09:30:00Z",
        "status": status,
    }


class CampaignLayerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="campaign-layer-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.kit_path = self.build_brand_kit()
        self.facts_path = self.build_facts()

    def build_brand_kit(self) -> Path:
        library = self.root / "library" / "brands"
        kit_path = BRAND_KIT.init_kit(library, "lumo", "Lumo")
        kit_dir = kit_path.parent
        logo = b"<svg xmlns='http://www.w3.org/2000/svg'><rect width='4' height='4'/></svg>"
        head = b"wOF2-head"
        body = b"wOF2-body"
        (kit_dir / "assets").mkdir(exist_ok=True)
        (kit_dir / "assets/logo.svg").write_bytes(logo)
        (kit_dir / "assets/head.woff2").write_bytes(head)
        (kit_dir / "assets/body.woff2").write_bytes(body)
        (kit_dir / "decisions/approve_v01.md").write_text("Approved after visible inspection.\n")
        kit = json.loads(kit_path.read_text())
        kit.update(
            {
                "source": {
                    "method": "website",
                    "urls": ["https://lumo.example/"],
                    "retrieved_at": "2026-10-17T09:00:00Z",
                    "authorized_by": "User states they own the brand",
                },
                "logos": [
                    {
                        "role": "primary",
                        "file": "assets/logo.svg",
                        "sha256": digest(logo),
                        "source": "user_supplied",
                        "min_height_px": 48,
                        "clear_space_ratio": 0.25,
                        "allowed_backgrounds": ["light"],
                    }
                ],
                "palette": [
                    {"name": "ember", "hex": "#D7261E", "role": "primary"},
                    {"name": "paper", "hex": "#FAFAFA", "role": "background"},
                    {"name": "ink", "hex": "#111111", "role": "text"},
                ],
                "typography": [
                    {
                        "role": role,
                        "family": family,
                        "weight": weight,
                        "file": f"assets/{name}.woff2",
                        "sha256": digest(data),
                        "source": "user_supplied",
                        "license": "Brand-supplied for advertising use",
                    }
                    for role, family, weight, name, data in (
                        ("headline", "Lumo Display", 700, "head", head),
                        ("body", "Lumo Text", 400, "body", body),
                    )
                ],
                "voice": {
                    "tone": ["warm"],
                    "reading_level": "plain",
                    "do": [],
                    "dont": [],
                },
                "copy_rules": {
                    "banned_words": ["cheap"],
                    "required_lines": [],
                    "trademark_marks": {},
                },
                "cta_style": {
                    "shape": "pill",
                    "case": "sentence",
                    "verbs": ["Shop now"],
                },
                "imagery": {
                    "style_sentence": "Soft window light on pale wood.",
                    "avoid": [],
                },
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
        kit_path.write_text(json.dumps(kit, indent=2))
        return Path(kit_path)

    def build_facts(self) -> Path:
        card = self.root / "elements" / "lumo-mug"
        card.mkdir(parents=True)
        image = b"\x89PNG\r\n\x1a\nsynthetic"
        (card / "ref_01_front.png").write_bytes(image)
        document = {
            "schema_version": 1,
            "product_id": "lumo-mug",
            "product_name": "Lumo travel mug",
            "brand_id": "lumo",
            "source": {
                "method": "product_page",
                "urls": [PAGE],
                "parse_status": "parsed",
            },
            "facts": [
                fact("f01", "Lid locks with one click", "supported"),
                fact("f02", "Dishwasher safe", "supported"),
                fact(
                    "f03",
                    "Makes coffee taste better",
                    "needs-substantiation",
                    "performance",
                ),
                fact("f04", "20% off this week", "perishable", "offer"),
            ],
            "images": [
                {
                    "file": "ref_01_front.png",
                    "source": "https://lumo.example/cdn/front.png",
                    "sha256": digest(image),
                    "retrieved_at": "2026-10-17T09:31:00Z",
                    "view": "front",
                }
            ],
        }
        path = card / "facts.json"
        path.write_text(json.dumps(document, indent=2))
        return path

    def spec(self, claims: list[str], layout: str = "hero-product") -> Path:
        spec = {
            "campaign": "lumo-launch",
            "language": "en",
            "brand_kit": str(self.kit_path.relative_to(self.root)),
            "brand_kit_sha256": BRAND_KIT.canonical_sha256(
                json.loads(self.kit_path.read_text())
            ),
            "facts": str(self.facts_path.relative_to(self.root)),
            "product": {
                "name": "Lumo travel mug",
                "image": "elements/lumo-mug/ref_01_front.png",
            },
            "output_dir": "statics",
            "layouts": [layout],
            "ratios": ["1:1", "9:16"],
            "angles": [
                {
                    "id": "one-click",
                    "type": "demonstration",
                    "headline": "Locks in one click",
                    "claims": claims,
                    "offer": "f04",
                    "terms": "Ends Sunday.",
                    "cta": "Shop now",
                }
            ],
        }
        path = self.root / "spec.json"
        path.write_text(json.dumps(spec))
        return path

    def test_brand_kit_and_facts_from_their_own_tools_validate(self) -> None:
        kit = json.loads(self.kit_path.read_text())
        kit_errors = BRAND_KIT.blocking(
            BRAND_KIT.validate_kit(kit, self.kit_path.parent)
        )
        self.assertEqual(kit_errors, [])
        facts = json.loads(self.facts_path.read_text())
        fact_errors = [
            finding
            for finding in PRODUCT_FACTS.validate_facts(
                facts, self.facts_path.parent, NOW
            )
            if finding.severity == "error"
        ]
        self.assertEqual(fact_errors, [])

    def test_static_batch_plans_from_validated_kit_and_facts_by_fact_id(self) -> None:
        result = STATIC_BATCH.plan(self.spec(["f01", "f02"]), self.root, False, now=NOW)
        names = sorted(job["name"] for job in result["jobs"])
        self.assertEqual(
            names,
            [
                "lumo-launch_one-click_hero-product_1x1_v01",
                "lumo-launch_one-click_hero-product_9x16_v01",
            ],
        )

    def test_static_batch_refuses_a_claim_the_facts_file_marks_unsupported(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            STATIC_BATCH.plan(self.spec(["f03"]), self.root, False, now=NOW)

    def test_offer_layout_plans_from_a_validated_perishable_offer_fact(self) -> None:
        facts = json.loads(self.facts_path.read_text())
        offer = next(fact for fact in facts["facts"] if fact["fact_id"] == "f04")
        self.assertEqual(offer["status"], "perishable")
        errors = [
            finding
            for finding in PRODUCT_FACTS.validate_facts(facts, self.facts_path.parent, NOW)
            if finding.severity == "error"
        ]
        self.assertEqual(errors, [])
        result = STATIC_BATCH.plan(self.spec(["f01"], "offer"), self.root, False, now=NOW)
        self.assertEqual(len(result["jobs"]), 2)
        self.assertEqual(result["jobs"][0]["copy"]["offer"], "20% off this week")
        self.assertEqual(result["jobs"][0]["claims"][0]["ref"], "f04")

    def test_offer_layout_refuses_the_same_offer_once_it_is_stale(self) -> None:
        later = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
        with self.assertRaisesRegex(ValueError, "stale"):
            STATIC_BATCH.plan(self.spec(["f01"], "offer"), self.root, False, now=later)


    def test_static_batch_and_product_facts_share_the_qualifier_list(self) -> None:
        def labels_and_patterns(module: ModuleType) -> list[tuple[str, str]]:
            return [(label, pattern.pattern) for label, pattern in module.QUALIFIERS]

        self.assertEqual(
            labels_and_patterns(STATIC_BATCH), labels_and_patterns(PRODUCT_FACTS)
        )

if __name__ == "__main__":
    unittest.main()

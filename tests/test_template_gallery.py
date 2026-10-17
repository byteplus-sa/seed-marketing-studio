import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
import template_gallery

PRESETS = """# Presets

### Rain Walk <!-- id: rain-walk -->
- Grammar: single-pass R2V
- Motion block: subject walks through light rain,
  umbrella tilting as the wind picks up
- Risks: puddle reflections flicker

### <script>alert(1)</script> & Co <!-- id: unsafe-title -->
- Job: show that "quotes" & <tags> are escaped.

```text
### Not An Entry <!-- id: fenced-entry -->
```
"""

EFFECTS = """# Effects

### `paper-fold` - Paper fold
**Look:** The room folds like a paper model around a still subject.
**Route:** i2v-first-frame.

### `data-attribute` - the attribute
Plain documentation, not a recipe card.
"""


class TemplateGalleryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="template-gallery-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.skills = self.root / "skills"
        self.write("motion-kit/references/presets.md", PRESETS)
        self.write("effects-kit/references/effects.md", EFFECTS)
        self.write("plain-skill/SKILL.md", "---\nname: plain-skill\n---\n# Plain\n")
        self.out = self.root / "gallery"

    def write(self, relative, text):
        path = self.skills / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_cli(self, *argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = template_gallery.main([str(item) for item in argv])
        return code, json.loads(output.getvalue())

    def build(self):
        code, result = self.run_cli("--skills-root", self.skills, "--out", self.out)
        self.assertEqual(code, 0, result)
        return result, (self.out / "index.html").read_text()

    def test_marked_entries_are_catalogued_with_preferred_summary(self):
        entries = {
            entry.entry_id: entry for entry in template_gallery.scan(self.skills)
        }
        rain = entries["rain-walk"]
        self.assertEqual((rain.skill, rain.title), ("motion-kit", "Rain Walk"))
        self.assertEqual(
            rain.summary,
            "Motion block: subject walks through light rain, umbrella tilting as "
            "the wind picks up",
        )
        self.assertEqual(rain.source, "motion-kit/references/presets.md")

    def test_recipe_code_headings_count_but_plain_code_headings_do_not(self):
        ids = {entry.entry_id for entry in template_gallery.scan(self.skills)}
        self.assertIn("paper-fold", ids)
        self.assertNotIn("data-attribute", ids)
        self.assertNotIn("fenced-entry", ids)
        paper = next(
            e for e in template_gallery.scan(self.skills) if e.entry_id == "paper-fold"
        )
        self.assertEqual(
            paper.summary,
            "Look: The room folds like a paper model around a still subject.",
        )

    def test_fenced_hash_lines_do_not_end_an_entry(self):
        self.write(
            "fence-kit/references/recipes.md",
            "# Recipes\n\n"
            "### `fence-card` - Fence card\n"
            "```bash\n# install step\nrun thing\n```\n"
            "**Look:** Text after the fence.\n\n"
            "### Tilde card <!-- id: tilde-card -->\n"
            "~~~markdown\n```\n## Not a heading\n~~~\n"
            "- Job: still part of the tilde card.\n",
        )
        entries = {
            entry.entry_id: entry
            for entry in template_gallery.scan(self.skills)
            if entry.skill == "fence-kit"
        }
        self.assertEqual(set(entries), {"fence-card", "tilde-card"})
        self.assertEqual(entries["fence-card"].summary, "Look: Text after the fence.")
        self.assertEqual(
            entries["tilde-card"].summary, "Job: still part of the tilde card."
        )

    def test_gallery_is_static_escaped_and_grouped_by_skill(self):
        result, page = self.build()
        self.assertEqual((result["skills"], result["entries"]), (2, 3))
        self.assertNotIn("<script", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; &amp; Co", page)
        self.assertIn("&quot;quotes&quot; &amp; &lt;tags&gt;", page)
        self.assertLess(page.index('id="effects-kit"'), page.index('id="motion-kit"'))
        self.assertIn('href="gallery.css"', page)
        self.assertTrue((self.out / "gallery.css").is_file())
        self.assertNotIn("plain-skill", page)

    def test_rebuild_is_deterministic(self):
        _, first = self.build()
        _, second = self.build()
        self.assertEqual(first, second)

    def test_duplicate_ids_within_a_skill_are_reported(self):
        self.write(
            "motion-kit/references/more.md",
            "### Again <!-- id: rain-walk -->\n- Job: x\n",
        )
        result, _ = self.build()
        self.assertEqual(result["duplicates"], ["motion-kit:rain-walk"])

    def test_empty_skills_root_writes_an_empty_gallery(self):
        empty = self.root / "empty"
        empty.mkdir()
        code, result = self.run_cli("--skills-root", empty, "--out", self.out)
        self.assertEqual(code, 0)
        self.assertEqual(result["entries"], 0)

    def test_missing_skills_root_is_refused(self):
        code, result = self.run_cli(
            "--skills-root", self.root / "nope", "--out", self.out
        )
        self.assertEqual(code, 1)
        self.assertFalse(result["ok"])
        self.assertFalse(self.out.exists())

    def test_output_inside_the_repository_is_refused_outside_projects(self):
        target = ROOT / ".agents" / "gallery-test-output"
        code, result = self.run_cli("--skills-root", self.skills, "--out", target)
        self.assertEqual(code, 1)
        self.assertIn("outside the repository", result["error"])
        self.assertFalse(target.exists())
        allowed = ROOT / "projects" / "demo" / "review"
        self.assertEqual(
            template_gallery.output_directory(allowed, ROOT / "projects"),
            allowed.resolve(),
        )

    def test_symlinked_documents_are_not_followed(self):
        outside = self.root / "outside.md"
        outside.write_text("### Leak <!-- id: leaked -->\n- Job: x\n")
        (self.skills / "motion-kit" / "references" / "link.md").symlink_to(outside)
        ids = {entry.entry_id for entry in template_gallery.scan(self.skills)}
        self.assertNotIn("leaked", ids)

    def test_repository_catalog_builds_without_errors(self):
        code, result = self.run_cli("--out", self.out)
        self.assertEqual(code, 0)
        self.assertGreater(result["entries"], 0)


if __name__ == "__main__":
    unittest.main()

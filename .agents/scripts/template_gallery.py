from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[2]
COMMENT_HEADING = re.compile(
    r"^(#{2,4})\s+(?P<title>.+?)\s*<!--\s*id:\s*(?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)\s*-->\s*$"
)
CODE_HEADING = re.compile(
    r"^(#{2,4})\s+`(?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)`\s+[-–—]\s+(?P<title>.+?)\s*$"
)
HEADING = re.compile(r"^(#{1,6})\s")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
RECIPE_LABEL = re.compile(r"^\*\*[A-Z][A-Za-z ]{0,30}:\*\*\s")
LIST_MARKER = re.compile(r"^(?:[-*+]|\d+\.)\s+")
LABEL = re.compile(r"^\*{0,2}([A-Za-z][A-Za-z ]{0,30}?)\*{0,2}:\*{0,2}\s")
PREFERRED_LABELS = (
    "look",
    "job",
    "motion block",
    "description",
    "use",
    "use when",
    "setting",
    "location",
)
SUMMARY_LIMIT = 280
STYLESHEET = """\
:root { color-scheme: light dark; --ink: #1d1d1f; --muted: #5f6368; \
--line: #d9dce1; --card: #ffffff; --page: #f5f6f8; }
@media (prefers-color-scheme: dark) { :root { --ink: #ececf1; --muted: #a1a5ad; \
--line: #3a3d44; --card: #1f2126; --page: #15171b; } }
* { box-sizing: border-box; }
body { margin: 0; padding: 24px 16px 48px; background: var(--page); color: var(--ink); \
font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1120px; margin: 0 auto; }
h1 { font-size: 1.6rem; margin: 0 0 4px; }
.note { color: var(--muted); margin: 0 0 24px; }
nav ul { display: flex; flex-wrap: wrap; gap: 8px 16px; padding: 0; list-style: none; }
nav a { color: inherit; }
section { margin-top: 32px; }
h2 { font-size: 1.2rem; border-bottom: 1px solid var(--line); padding-bottom: 4px; }
.grid { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
article { background: var(--card); border: 1px solid var(--line); border-radius: 8px; \
padding: 12px 14px; }
article h3 { font-size: 1rem; margin: 0 0 2px; }
code { font-size: 0.85rem; color: var(--muted); overflow-wrap: anywhere; }
article p { margin: 8px 0 0; }
.source { display: block; margin-top: 8px; font-size: 0.75rem; }
"""


@dataclass(frozen=True)
class Entry:
    skill: str
    entry_id: str
    title: str
    summary: str
    source: str
    line: int


def clean(text: str) -> str:
    text = LIST_MARKER.sub("", text.strip())
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("`", "")).strip()


def closes_fence(line: str, opener: str) -> bool:
    match = FENCE.match(line)
    return bool(
        match
        and match.group(1)[0] == opener[0]
        and len(match.group(1)) >= len(opener)
        and not line[match.end() :].strip()
    )


def fence_mask(lines: list[str]) -> list[bool]:
    mask: list[bool] = []
    opener = ""
    for line in lines:
        if opener:
            mask.append(True)
            if closes_fence(line, opener):
                opener = ""
            continue
        match = FENCE.match(line)
        opener = match.group(1) if match else ""
        mask.append(bool(match))
    return mask


def blocks(lines: list[str]) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    for line, fenced in zip(lines, fence_mask(lines)):
        if fenced:
            continue
        stripped = line.strip()
        starts = (
            not stripped
            or LIST_MARKER.match(stripped)
            or RECIPE_LABEL.match(stripped)
            or stripped.startswith("|")
        )
        if starts and current:
            result.append(" ".join(current))
            current = []
        if stripped and not stripped.startswith(("|", "<!--")):
            current.append(stripped)
    if current:
        result.append(" ".join(current))
    return result


def label_of(block: str) -> str:
    match = LABEL.match(LIST_MARKER.sub("", block))
    return match.group(1).strip().lower() if match else ""


def summary_of(lines: list[str]) -> str:
    candidates = blocks(lines)
    if not candidates:
        return ""
    chosen = next(
        (
            block
            for label in PREFERRED_LABELS
            for block in candidates
            if label_of(block) == label
        ),
        candidates[0],
    )
    text = clean(chosen)
    return text if len(text) <= SUMMARY_LIMIT else text[: SUMMARY_LIMIT - 1] + "…"


def entry_heading(line: str) -> tuple[int, str, str, bool] | None:
    match = COMMENT_HEADING.match(line) or CODE_HEADING.match(line)
    if not match:
        return None
    marked = match.re is COMMENT_HEADING
    return len(match.group(1)), match.group("id"), clean(match.group("title")), marked


def scan_document(skill: str, path: Path, source: str) -> list[Entry]:
    lines = path.read_text(encoding="utf-8").splitlines()
    fenced = fence_mask(lines)
    entries: list[Entry] = []
    for index, line in enumerate(lines):
        heading = None if fenced[index] else entry_heading(line)
        if heading is None:
            continue
        level, entry_id, title, marked = heading
        end = next(
            (
                position
                for position in range(index + 1, len(lines))
                if not fenced[position]
                and (match := HEADING.match(lines[position]))
                and len(match.group(1)) <= level
            ),
            len(lines),
        )
        body = [
            text
            for position, text in enumerate(lines[index + 1 : end], index + 1)
            if fenced[position] or not HEADING.match(text)
        ]
        labelled = any(
            not fenced[position] and RECIPE_LABEL.match(lines[position])
            for position in range(index + 1, end)
        )
        if not marked and not labelled:
            continue
        entries.append(
            Entry(skill, entry_id, title, summary_of(body), source, index + 1)
        )
    return entries


def scan(skills_root: Path) -> list[Entry]:
    entries: list[Entry] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        for document in sorted(skill_dir.rglob("*.md")):
            if document.is_symlink() or not document.resolve().is_relative_to(
                skills_root.resolve()
            ):
                continue
            source = document.relative_to(skills_root).as_posix()
            entries.extend(scan_document(skill_dir.name, document, source))
    return entries


def duplicates(entries: list[Entry]) -> list[str]:
    seen: set[tuple[str, str]] = set()
    repeated: set[str] = set()
    for entry in entries:
        key = (entry.skill, entry.entry_id)
        if key in seen:
            repeated.add(f"{entry.skill}:{entry.entry_id}")
        seen.add(key)
    return sorted(repeated)


def render_entry(entry: Entry) -> str:
    summary = f"<p>{html.escape(entry.summary)}</p>" if entry.summary else ""
    return (
        f'<article id="{html.escape(entry.skill)}--{html.escape(entry.entry_id)}">'
        f"<h3>{html.escape(entry.title)}</h3>"
        f"<code>{html.escape(entry.entry_id)}</code>{summary}"
        f'<code class="source">{html.escape(entry.source)}:{entry.line}</code>'
        "</article>"
    )


def render(entries: list[Entry]) -> str:
    skills = sorted({entry.skill for entry in entries})
    nav = "".join(
        f'<li><a href="#{html.escape(skill)}">{html.escape(skill)}</a> '
        f"({sum(entry.skill == skill for entry in entries)})</li>"
        for skill in skills
    )
    sections = "".join(
        f'<section id="{html.escape(skill)}"><h2>{html.escape(skill)}</h2>'
        '<div class="grid">'
        + "".join(render_entry(entry) for entry in entries if entry.skill == skill)
        + "</div></section>"
        for skill in skills
    )
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>Template Gallery</title>"
        '<link rel="stylesheet" href="gallery.css"></head><body><main>'
        "<h1>Template Gallery</h1>"
        f'<p class="note">{len(entries)} presets, hooks, effects and modes from '
        f"{len(skills)} skills. A visual aid only; the skill references are the "
        "source of truth.</p>"
        f"<nav><ul>{nav}</ul></nav>{sections}</main></body></html>\n"
    )


def output_directory(value: Path, allow_inside: Path) -> Path:
    target = value.resolve()
    if target.is_relative_to(REPOSITORY) and not target.is_relative_to(allow_inside):
        raise ValueError(
            "Output must be outside the repository or under projects/<name>/review"
        )
    return target


def write_gallery(skills_root: Path, out: Path) -> dict[str, object]:
    if not skills_root.is_dir():
        raise ValueError(f"Skills root does not exist: {skills_root}")
    entries = scan(skills_root)
    target = output_directory(out, REPOSITORY / "projects")
    target.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "gallery.css"):
        if (target / name).is_symlink():
            raise ValueError(f"Refusing to write through a symlink: {name}")
    (target / "index.html").write_text(render(entries), encoding="utf-8")
    (target / "gallery.css").write_text(STYLESHEET, encoding="utf-8")
    return {
        "output": str(target / "index.html"),
        "skills": len({entry.skill for entry in entries}),
        "entries": len(entries),
        "duplicates": duplicates(entries),
    }


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(
        description="Write a static HTML catalog of preset, hook, effect and mode entries"
    )
    cli.add_argument("--out", type=Path, required=True)
    cli.add_argument("--skills-root", type=Path, default=REPOSITORY / ".agents/skills")
    args = cli.parse_args(argv)
    try:
        result = write_gallery(args.skills_root, args.out)
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2))
        return 1
    print(json.dumps({"ok": True, **result}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

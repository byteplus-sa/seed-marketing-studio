# Input Format

Read [the entrypoint](../SKILL.md).

## Timing JSON

Keep one small JSON per clip, or one per cut, under
`projects/<campaign>/captions/`.

```json
{
  "schema_version": 1,
  "offset_s": 6.2,
  "lines": [
    {
      "id": "vo-01",
      "speaker": "voiceover",
      "start_s": 0.4,
      "end_s": 2.6,
      "text": {
        "en": "Cold for up to 24 hours. Hot for up to 12.",
        "es": "Frío hasta 24 horas. Caliente hasta 12."
      }
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `schema_version` | Must be `1` |
| `offset_s` | Optional. Where this file's time zero sits on the cut's timeline |
| `lines[].id` | Optional stable id used in warnings; defaults to `<file-stem>-line-NNN`. Ids must be unique across every `--input` file |
| `lines[].speaker` | Optional nonempty label (presenter, voiceover); never printed |
| `lines[].start_s`, `end_s` | Seconds from the file's zero; `end_s` after `start_s` |
| `lines[].text` | Object keyed by language code: the locked text per language |

Final time = `start_s` + `offset_s` + the command-line `--offset-s`.

## Where each value comes from

| Value | Source |
| --- | --- |
| `text` | The locked ad script and its approved translations; claims, prices, names and qualifiers ("up to", "from") exactly as approved, never shortened into a stronger claim |
| `start_s`, `end_s` | Speech-to-text segment or word times on the placed take or voiceover, confirmed by listening |
| `offset_s` | The clip's `data-start` on the cut's Studio timeline, never a sum of planned durations |

Each delivered cut has its own timeline. A cutdown (for example a 6 s bumper)
needs its own timing file; never reuse the long cut's offsets.

## Output behavior

- Cues are sorted by start time; overlaps are trimmed to the later cue's start
  minus the gap (`--overlap error` stops instead).
- Short cues are extended toward the minimum duration and reading-speed need,
  never past the next cue or the master duration.
- A cue longer than the maximum duration, or with more text than fits the line
  limits, splits at clause punctuation or token boundaries with time shared by
  text length.
- All outputs are planned before any file is written, so a failure in one
  language writes nothing.

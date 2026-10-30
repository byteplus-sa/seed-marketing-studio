# Output Templates

Focused reference for `seedance-music-video`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [Output formats](#output-formats)

## Output formats

Adapt the fields to the brief. Custom treatments, coherent hybrids and planned
section transitions do not need recipe labels. Summaries are optional; omit
redundant fields for scoped edits. Use only the shots or stages needed, with
no numeric shot-duration floor. Preserve requested timing; use assembly for
frame-exact cuts when authorized, and surface conflicts with locked workflows.

### Music-video block

Use when the user only wants the directing layer:

```text
[Music-Video Format]
<Format name, direct or indirect address, and performance-to-atmosphere ratio.>

[Song Map]
Section 1 (<verified time range or event cue>): <visual assignment, energy, end state>.
Section 2 (<verified time range or event cue>): <visual assignment, energy, end state>.
Final Section (<verified time range or event cue>): <closing assignment and final visible state>.

[Beat & Cut Contract]
<Which audio events the cuts and camera land on; cut density per section.>

[Audio Treatment]
<Native audio, a selected supported timing reference, or silent picture with
the authorized master or requested bed added in post. State unresolved support.
Prefer direct @Audio N when supported; a black-sync carrier is optional only
when supported and selected for this request.>

[Visual Treatment]
<Brief-derived palette, lighting, camera, cadence and tone; scope any transitions.>

[Treatment Summary] (optional)
<Compact continuity and transition summary; exclusions only for actual conflicts.>
```

### Full Seedance prompt

Use when the user asks for a complete prompt:

```text
[Song Timing Authority] (only with a selected, supported reference)
<Verified reference binding> supplies the authorized master segment.
Its vocals, pauses and musical accents guide the performance and pacing.
Match <performer>'s visible mouth only to their voice during designated
lip-synced phrases. Keep generated imagery text-free.
(Direct audio uses @Audio N. An optional supported carrier uses its actual
@Video N binding and supplies timing, not its black picture. In an edit,
@Video 1 remains the source scene. Preserve the exact master for post;
reference conditioning does not guarantee copied audio or exact mouth timing.)

[Reference Roles] (only when references exist)
@Image 1 defines <performer>'s <appearance, wardrobe, or identity>.
@Image 2 defines <scene or venue>. Do not use <unwanted content>.

<Subject performs the primary action in <scene>.>
The visuals feature <brief-derived treatment: palette, lighting, lens, grade, look>.
Use <shot sizes, camera moves, and cuts>, with <beat contract>.
Audio: <selected timing binding, native brackets, or silent picture for post>.
For native audio: <(music)> <{sung lines}> <sound effects>.
For rap or fast vocals,
       use verified per-line timing when available, otherwise ordered cues: <[X-Ys] { line }> per line with a
       "no line skipped" mandate (see section 3b).

[Shot Plan] or [Stage Plan]
Shot 1 (<verified time range or event cue>): <size>, <angle>, <lens intent>; <camera move or motivated hold>. <critical ordered actions, reveals or sustained state, their intent, and the visible end state>. Light: <named source, key side>.
Shot 2 (<time range>): <size>, <angle>, <lens intent>; <camera move>. <critical ordered actions, reveals or sustained state, their intent, and the visible end state>. Light: <named source, key side>.
Final Shot (<time range>): <size>, <angle>, <lens intent>; <camera move>. <closing action and final visible state>. Light: <named source, key side>.

[Maintain Consistency]
Preserve <source locks, approved identity, wardrobe, venue and exact audio>.
Keep shared choices consistent except for authorized section-specific changes.
For preservation-only edits, retain source camera, cuts, actions and mouth motion.

[Treatment Summary] (optional)
<Compact treatment, beat relationship, continuity and intended transitions.>
```

Return the prompt directly. Do not add production workflow, tool selection,
asset management, approval gates, or generation instructions unless the user
explicitly asks for them.

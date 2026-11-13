# Music Video and UGC Checklist

Song-driven Seedance prompts and UGC hook and script drafts. Apply the universal
items in [the index](review-checklists.md#universal--all-prompts) first.

## Seedance music video

Source skill: `seedance-music-video`

This additive layer preserves musical intent and exact master/lyric fidelity.
Resolve the selected model and operation first. Adapter syntax, reference roles
and duration limits apply only when verified for that exact binding. Otherwise
record `not_applicable` for adapter grammar, retain ordinary language sound
intent and leave executable settings unresolved. Genre never selects an adapter.

### Format and genre

1. **Format declared.** Performance, narrative, conceptual, lyric, visualizer,
   or hybrid — with address mode (direct / indirect / none).

2. **Treatment serves intent.** Preserve approved visual choices. Format and
   style are brief-derived, following the desired audience effect and available
   track evidence. Custom treatments and coherent hybrids are valid; genre
   recipes are optional examples, not compulsory locks or a ban on coherent hybrids.

### Song map

3. **Readable section intent.** A section may carry ordered events, reveals or
   sustained attention. Check causal order and perceptual outcomes without a
   single-event quota; preserve locked action, reveal timing and stillness.

4. **Repeated sections have an intentional relationship.** Escalation, restraint,
   repetition or counterpoint follows supplied audible changes or the requested
   effect. A quiet return need not become larger or faster.

5. **Structure is evidenced.** Do not invent a bridge or assume it requires a
   new location, wardrobe or angle. Label a plan provisional when no track or
   user section map supports exact structural claims.

### Audio contract

6. **Audio treatment explicit.** Name native sound, an exact master, post audio,
   silence or owned mixed layers. Native brackets and `@Audio N` roles are
   conditional on the selected operation, not required for ordinary language
   prompt-only intent. Separate audio generation remains opt-in.

7. **Lip-sync lines verbatim.** Match the audio master exactly:
   no paraphrasing, reordering or omitted lines. Use `{...}` only when the
   selected adapter and operation support that syntax.

8. **Lyric timing follows audio evidence.** When coverage or synchronization
   requires per-line timing, use audio-measured cues, retaining
   raw measurements separately from proposed edits. With unavailable audio or
   unverified timings, use ordered cues and label timing provisional. Genre or
   fast delivery alone does not require timestamps or justify invented timings.
   `[X-Ys] { line }` slots apply only to a verified compatible adapter.

9. **"No line skipped" mandate present.** When the timestamped timeline is
   used, the prompt includes an explicit instruction that no line may be
   skipped, shortened, mumbled, or reordered.

10. **Native audio caveat acknowledged.** If `generate_audio` is true, the
    prompt accounts for re-performance risk (the model re-performs, not copies,
    the reference).

### Beat contract

11. **Audio events named.** Which beats trigger cuts and camera moves —
    not just "cuts on the beat."

12. **Cuts follow intent and evidence.** Do not assume verses are quiet, choruses
    are loud, or every edit precedes a downbeat. Preserve continuous performance
    and unmetered pauses when requested; keep raw timing separate from simplification.

### Structure

13. **Right-sized to intent and verified limits.** Preserve requested section
    spans, fractional beats and continuous takes. The historical 4–30s adapter
    range applies only to its verified selected operation; unknown limits stay
    unresolved. Do not pad, round or split to satisfy an inapplicable range.

14. **Treatment summary is optional.** When useful, summarize brief-derived
    continuity, coherent hybrid choices and deliberate section transitions.
    Preserve an approved single-style treatment; judge fidelity and readable
    transitions, not a mandatory genre lock or style-seal phrase.

### Rap-specific (when applicable)

15. **Timing is proportional.** Use source-grounded lyric timing when coverage
    or synchronization requires it; rap genre alone does not mandate timestamps.
    Do not invent beat timings or claim to have listened to unavailable audio.

16. **Delivery cue present.** The prompt includes a physical delivery cue
    (e.g., "jaw opening fully on vowels, lips stay in frame throughout").

---

## UGC hooks and scripts

1. **Product truth.** Trace numerical, comparison, performance and personal-use
   claims to supplied evidence. No invented trial duration, testimonial, saving
   or demonstrated result. Missing facts allow a truthful demonstration angle.
2. **Audience objection.** The hook addresses the supplied concern using a
   supported feature or proposed demonstration, not unrelated hype.
3. **Distinct angles.** Requested alternatives differ in persuasive mechanism
   or objection addressed; synonym swaps alone do not make distinct concepts.
4. **CTA fidelity.** Preserve the supplied offer and destination. Do not invent
   a discount, guarantee, scarcity claim or purchase experience.
5. **Mode respects scope.** Hooks/scripts can be completed without generating
   assets. Hypothetical actors are not evidence of real customer experiences.

# Seedance Legacy Checklist

Seedance 2.0 generation (4K, Fast, Mini) and the legacy video-to-video VFX path.
Apply the universal items in [the
index](review-checklists.md#universal--all-prompts) first.

## Seedance 2.0

Source skill: `seedance-prompt`

This section preserves useful 2.0 review history, not a second prompt
entrypoint. Apply [family review](checklist-seedance-family.md) first.
Validate executable limits and syntax for the selected exact operation; unknown
evidence stays unresolved. General creative structure remains flexible.

### Structure

1. **Readable structure.** Roles, stable subjects, intended task, ordered action
   and preservation constraints are clear. Legacy section headings are optional.

2. **Ordered reference mapping.** Each selected reference has an explicit role
   and stable typed label. Verify destination syntax before execution; a
   separate asset-preparation heading is optional.

3. **Reference limits.** Verify counts, sizes, duration and combined roles against
   the exact model, operation and destination, not an inherited 2.0 table.

### Subject definitions

4. **Stable identities.** Distinguishing static features identify each subject;
   `Define` is optional. Do not confuse temporary expression or pose with identity.

5. **Label reuse.** Stable subject labels and reference order carry across shots
   without unnecessary repetition of the full mapping.

6. **Readable bindings.** Provider asset IDs stay in the separate binding
   package; readable typed references identify subjects in the prompt.

### Reference classification

7. **Classification.** Each reference is classified as: Visible identity, Visible
   environment, Motion/camera reference, or Control-only reference.

8. **Control-only handling.** Translate planning maps and boards to text and omit
   them. Labels do not establish input eligibility or authorization.

9. **Face restriction.** No direct uploads of real human faces. Uses recent model
   outputs, preset digital characters, or authorized `asset://` portrait
   assets (CRITICAL when a raw real-person photo is bound).

9a. **No storyboard binding (`references.no_board_binding`).** Board panels and
   grids are never bound; their staging is written in the shot lines (CRITICAL
   when bound).

### Task type declaration

10. **Task intent clear.** Distinguish reference-guided generation, source
    editing and extension. API task types require exact-operation evidence.

11. **Edit/extend phrasing.** Identify the source as the editing master or the
    boundary to extend, not merely a motion reference. A phrase does not
    guarantee mode selection; verify supported task controls separately.

### Shots

12. **Readable sequence.** Shots or optional stages communicate ordered actions
    or a sustained state. Numbered headings are aids, not acceptance criteria.

12a. **Shot plan carried (`shot.plan_bound`, `shot.variety`, `shot.axis_carry`).**
    The Seedance 2.5 shot-plan items (`shot.plan_bound`, `shot.variety`, `shot.axis_carry` in [the 2.5 checklist](checklist-seedance-25.md#shot-plan-and-structure)) apply to a 2.0 prompt: each shot line carries
    its size, angle, camera move (or a recorded static reason) and a declared
    light source with its key side. Contrast, cadence, turns and standout images
    are optional; repeated framing, constant light and sustained holds pass
    when they serve the approved intent and readability.

13. **Reference continuity.** Each shot unambiguously identifies the relevant
    subjects and inherited reference authority; a clear shared mapping suffices.

14. **Per-shot facts.** Preserve planned camera, action, spatial changes,
    lighting and audio where applicable. Their prose order is flexible.

15. **Coherent camera movement.** One or two moves is a planning heuristic,
    not a cap on coherent requested choreography. Check sequence, endpoints
    and readability; flag incompatible simultaneous directions or unclear
    handoffs, not move count alone.

16. **Feasibility.** Assess causal order, readable action and actual timing.
    No beat or shot quota applies. Splitting is an unselected alternative,
    not permission to drop actions or add paid clips.

17. **Action detail.** Include body-part, range, speed or force details only when
    they communicate critical action or continuity.

18. **Motion intent.** Body speed, amplitude, interruptions and recovery follow
    the approved action. Quiet performance and repeated bursts are valid;
    evaluate readability, contact and balance, not a low-energy default or a
    burst-count cap. Slowing motion or separating a burst with holds is an
    optional repair for a demonstrated failure. Speech does not impose an
    energy ceiling on actor, camera or edit rhythm; check required delivery,
    lip-sync and listener evidence at the actual framing and speed.

19. **Emotion externalization.** Emotions are externalized as physical details,
    never bare labels.

20. **Dialogue format and budget (`dialogue.speech_budget`).** Preserve exact
    words and speaker ownership. Quotes or documented bracket cues distinguish
    speech; verify syntax and lip-sync support separately. Use measured delivery or a native-language-informed read with
    pauses, onset and tail. Words / 2.2 is an English planning estimate, not a
    universal rejection rule. Initially allow 0.5-1.5 s onset and at least
    0.4 s tail, then verify actual delivery; without evidence, fit is provisional.
    Preserve approved text; propose retiming or splitting before an authorized
    wording change.

### Timing

21. **Duration separate.** Keep executable duration controls outside the
    creative prompt and verify them for the exact operation. Creative timing
    and source spans do not establish API support.

22. **Optional timing.** Add timing when requested or needed for critical
    handoffs; do not require a timestamp for every action.

23. **Timestamp format.** If used: concise ranges (`Shot 1 (0-4s):`), contiguous,
    non-overlapping, consistent with creative duration. Unverified executable
    duration remains unresolved.

### Spatial continuity

24. **Spatial facts present.** Movement-heavy scenes state Start, Travel axis,
    Subject order, Boundary behavior, End and relevant Forbidden transitions.
    The six-field format is optional; preserve the physical relationships.

25. **Physical locations.** Uses physical locations and ordered states, not relative
    verbs alone.

### Quality and constraints

26. **Inline constraints.** Keep necessary preservation exclusions in the prompt;
    do not invent a separate negative-prompt field without operation evidence.

27. **Prioritized constraints.** Prioritizes constraints instead of accumulating a
    long blacklist.

28. **Positive phrasing.** States required physical behavior positively. Repeats only
    the few exclusions that prevent expensive failure.

### Preflight review (6-point)

29. **Parameter agreement.** Prompt and API resolution, duration, ratio, and audio
    setting agree.

30. **Reference indexing.** Every reference is indexed, classified, and bound only
    where intended.

31. **Spatial fields.** Start, travel axis, subject order, boundary behavior, and end
    state are explicit.

32. **No contradictions.** No contradictory instructions (e.g., "single continuous
    shot" plus several cuts; "no powers" plus an emitting aura reference).

33. **Focus.** Prompt is focused; repetition compressed before removing critical
    spatial state.

34. **Beats fit duration.** Assess requested beats against actual timing and
    visibility. Missing evidence stays unresolved; a split needs authorization
    and never silently changes locked source timing or single-clip scope.

### Revision contract (if revising)

35. **Locked decisions carried.** Approved identity, action, camera, environment,
    audio, boundary behavior carried into revised prompt.

36. **Scoped delta.** Change only the requested behavior. Isolate prompt wording,
    reference bundle or motion design when practical to diagnose a repair;
    necessary linked changes remain explicit and within authorization.

37. **Acceptance criteria.** Observable conditions for the next take to pass are
    stated.

38. **Known rejections.** Behaviors from earlier takes that must not return are listed.

---

## Seedance VFX (video-to-video)

Source skill: `seedance-vfx-prompt`

### Core principle

1. **Source clip is the lock.** The prompt preserves what to keep (subject identity,
   performance, camera motion) and describes only what should change. It does not
   re-describe the entire scene from scratch.

### Asset preparation

2. **@Video 1 is source.** Source clip is always `@Video 1`. Uses "Strictly edit
   @Video 1" (NOT "Reference @Video 1").

3. **Source described.** Subject, action, camera motion, and duration of source clip
   are described in asset preparation.

4. **Source inspected.** The source clip was inspected before writing (duration, fps,
   aspect ratio probed). Prompt is built from footage, not user's one-line summary.

5. **Texture references labeled.** Texture references say "texture only" — "appearance
   and fur/skin texture reference only; ignore the photo's background and lighting."

### Subject definitions

6. **Define keyword.** Uses `Define` with 2-3 core static features. Bound as
   `<Label>@Video 1`.

### Locks (preservation)

7. **Locks declared.** Identity (face, body, costume, props), Performance (gait,
   gestures, expressions, timing), Camera (motion type, framing, lens, bob),
   Continuity are locked with `<Label>@Video 1`.

### Change

8. **Change named with timestamp.** The exact change and when it happens are stated
   (`At 0:NN` for localized changes). Global changes at `0:00`.

9. **Subject reaction.** Whether the subject reacts or does not react is stated.

### New world

10. **Full description.** Replacement/added environment/element is fully described.

### Lighting (embedded)

11. **Lighting lives in the world.** Light sources are physically present in the new
    world. Not described as a layer pasted on top.

12. **No generic lighting terms.** Does not say "cinematic lighting" or "dramatic
    lighting" alone — names the source.

13. **Light on subject.** Where light falls on subject (direction, color, intensity)
    is described.

14. **Light-environment interaction.** How light interacts with environment
    (volumetric mist, reflections, shadows) is described.

15. **Integration fork decided.** Either "preserve subject's lighting; grade only new
    elements" (default) OR "relight the whole frame under one look" is explicitly
    chosen.

16. **"Looks pasted in" recipe applied.** Light (direction, softness, shadow density),
    environmental bounce, optics & atmosphere (lens, micro-contrast, haze, DOF, grain),
    edges & grounding (no hard cut-out, no halos, matched rims) are addressed.

### Space

17. **Layered space.** Foreground (parallax elements), Midground (subject + primary
    environment), Background (atmosphere and scale) are described.

### Timing

18. **Sequential timestamps.** When each event triggers and how it progresses.

19. **Timed camera moves dual-anchored.** Semantic anchor ("At the line '<exact
    words>,' the camera <move>") AND numeric anchor ("At about <T> seconds...").

20. **Zoom type specified.** Crash zoom = fast hard punch-in. Smooth push-in = slow
    steady glide.

21. **Tail after trigger.** Enough tail (~2-3s) after trigger for payoff. If clip is
    short, zoom fires on first word.

22. **Reveal pull-back.** If used: opens tight on added element, moves outward to land
    on real plate, demands 100% match of source composition at landing.

23. **Lip-sync window checked.** If lip-sync preservation: line quoted verbatim,
    anchored twice (in change/action and in audio), `SFX and source dialogue only`
    requested, "lips matching the source exactly" in Locks, line fits surviving
    dialogue window.

### Audio

24. **Diegetic only.** Only sound that physically exists in the new world. Preserves
    source-clip diegetic sounds that still make sense.

25. **No non-diegetic audio.** Does not request background music, score, or voiceover
    unless part of source footage.

### Quality and constraints

26. **NON-IP.** No recognizable real persons, no copyrighted characters, no brand logos.

27. **Face protection.** "Real human skin with pores, stubble, and catchlights — never
    waxy, smoothed, or warped."

28. **Supported model/mode (`model.supported_mode`).** Resolve operation and
    model first. A 2.5 face-containing edit uses supported 480p/720p/1080p;
    only an explicitly selected supported legacy path may use 4K. Face/detail
    fidelity is an output-QA criterion, not a guaranteed property of resolution.

### Creature/element integration (if applicable)

29. **Photoreal demanded.** "Fully photoreal, real fur with depth and individual
    strands, true anatomy, never CG, plastic, or cartoonish."

30. **Tied into plate.** Same sun direction, real soft-edged contact shadow, same hazy
    atmosphere.

31. **Scale explicit.** Scale is explicit for giant creatures.

32. **Texture fallback.** If still reads CG: second input — reference photo of real
    animal as texture-only `@Image N`.

33. **Species behavior.** Behavior matches the species (sloth slow, chimp twitchy,
    snake coils and forked tongue, snakes don't blink).

34. **Living micro-movements.** For static creature holds: slow blink, jaw shift,
    steady breath.

### Duration discipline

35. **Source runtime default.** Defaults to source clip's exact runtime.

36. **Recomputed timing.** If runtime changed, numeric zoom timing is recomputed.

37. **Prepended-intro budget.** `total runtime − intro length = surviving window for
    source performance`. If source take longer than surviving window, one of three
    resolutions offered (extend total, start source earlier, accept truncation).

### Iteration discipline

38. **Only named change.** Only the named thing changes; rest of prompt stays stable.

39. **Refine via edit.** When refining a generated still/frame, edits the chosen result
    (passes it back as base) and fixes only what is off.

### Voice

40. **No generic adjectives.** No "beautiful," "stunning," "amazing," "cinematic."

41. **Concrete language.** Names exact materials, behaviors, scale, lenses, angles,
    moves. Uses texture words. Does not inflate, soften, or explain what things
    "represent."

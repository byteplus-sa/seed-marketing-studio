# Ad prompt worked repairs

All cases are **hypothetical**. Failures are simulated editorial diagnoses, not
observed generated-media behavior or measured advertising results.

## Invented numerical hook and experience

- **Brief:** A travel bottle has a flip latch and a removable carrying loop.
  Target commuters who wonder how it clips to a bag. Fifteen seconds, casual
  demonstration, CTA: "See the attachment guide." No price or user review supplied.
- **Initial prompt:** "I replaced fourteen bottles and saved $180 in two weeks."
  Presenter raises the bottle and says it changed her commute.
- **Simulated failure:** The opening invents numbers and personal history, and
  never answers the supplied attachment question. A generated presenter proves none of it.
- **Smallest repair:** "Here is where the carrying loop attaches." Hold the loop
  and its connection point in one view; show the supported attachment operation,
  then keep the supplied CTA. Omit savings and experience assertions.
- **Tradeoff:** Loses sensational specificity; gains an answer grounded in known
  facts. If attachment steps are unknown, request the guide before detailing them.
- **Acceptance:** Every spoken fact is supported, the connection is visible, and
  the CTA remains verbatim. The render is illustrative, not proof of durability.

## Three hooks that repeat the same persuasion

- **Brief:** Explore hooks for a lamp with a swiveling head and touch brightness
  control. Audience: small-desk users; hypothesized objection: where to aim light.
- **Initial hooks:** "You need this lamp"; "Your desk needs this"; "Get this for your desk."
- **Simulated failure:** The wording changes, but each offers the same unsupported appeal.
- **Smallest repair:** Demonstration: show the head swivel from notebook to keyboard.
  Objection: "Want the light aimed here?" followed by the same supported adjustment.
  Discovery: a close view reveals the supplied touch control and its operation.
- **Tradeoff:** The discovery angle explores a different known feature; it may be
  less aligned with the hypothesized aiming objection. Test the hypothesis rather
  than claiming an angle is a proven winner. Do not invent size or energy savings.
- **Acceptance:** Each has a distinct viewer question and visible payoff, with
  identical fact boundaries. Only the selected hook enters a final prompt.

## Requested honest con with no evidence

- **Brief:** Review a skincare device in a bathroom; include one honest con.
  No experience, efficacy data, or limitation has been supplied.
- **Initial prompt:** "It irritated my skin for three days, but now my wrinkles are gone."
- **Simulated failure:** Both the drawback and benefit invent bodily outcomes and testimony.
- **Smallest repair:** Ask which actual limitation and approved experience to use.
  Meanwhile draft neutral framing and a feature demonstration using supplied facts;
  label the verdict unresolved outside the spoken prompt.
- **Tradeoff:** A finished testimonial waits for evidence, but camera and scene
  development can proceed without inventing a user's experience.
- **Acceptance:** No unsupported efficacy, history, or con appears in dialogue;
  the missing evidence is precisely identified rather than buried in a placeholder.

## Phone-shot demo that breaks the generation rules

- **Brief:** Fifteen-second `ugc-how-to` for a refill bottle with three
  stackable flavour pods. Supplied fact: pods click into the lid. CTA: "Find
  your flavour." Product reference sheet supplied for the bottle only.
- **Initial prompt:** "She picks up the bottle with her left hand, drops three
  pods in (more pods in the drawer), sips from her logo mug and says {45 words}.
  Caption 'SHOP NOW' at the end."
- **Simulated failure:** Assume English delivery at 2.2 words/s for this
  fictional example: 45 / 2.2 is about 20.5 s before onset and tail, so the
  15 s plan risks a cut-off CTA; this is not a universal rejection rule.
  Measured or native-language-informed delivery determines fit. "Left hand"
  can mirror; the drawer invites a fourth pod; the
  mug grows invented lettering; the caption is rendered as garbled text.
- **Smallest repair:**

  This example assumes the draft copy is editable. Preserve approved text in
  real tasks; propose retiming or splitting before an authorized rewrite.

  Request a pod reference showing each pod's appearance and an operating guide
  establishing insertion order, contact points and the completed stack. The
  bottle reference does not establish these facts. Do not invent pod colours,
  sizes or a working insertion sequence.

  Until those inputs arrive, return only this provisional non-operational
  direction, not a generation-ready demonstration:

  ```text
  @Image 1 defines only the refill bottle: shape, colour, material and its
  printed label. Casual phone-shot in a bright kitchen, eye-level medium shot,
  the phone held steady on a fixed framing. Soft daylight from a window
  frame-left keys her face and the bottle.
  Keep the requested left hand holding the bottle, frame-right in this
  unmirrored front-facing view. Show only the bottle's evidenced orientation.
  Proposed copy: "Three pods, one bottle. Find your flavour."
  Audio direction: room tone and conversational voice.
  ```

  Reserve 4-10 s provisionally for the demonstration, dependent on the missing
  evidence. Once supplied, bind it and track exactly three pods across counter,
  hand and lid; never add a fourth. Target a CTA finish near 13.5 s and a held
  tail to 15 s, subject to actual speech QA. The caption moves to finishing;
  the static camera is recorded as `format_static_by_design`.
- **Tradeoff:** The operational prompt remains incomplete until its inputs
  exist; simpler copy provides planning room but does not prove audibility.
- **Acceptance:** Before generation, confirm pod identity and operating steps.
  After generation, inspect counts and anatomical hand/frame-side continuity,
  listen for complete dialogue, and verify the CTA ends before the clip.
  No generated overlay text; physical product markings match their references.

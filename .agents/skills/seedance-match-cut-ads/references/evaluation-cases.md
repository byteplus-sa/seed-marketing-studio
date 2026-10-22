# Evaluation Cases

Read when testing or changing this skill. Evaluate offline responses against
these hypothetical briefs. Do not generate footage, edit a source or claim
perceptual validation from this exercise. Record the actual answer and which
assertions it satisfies; any forbidden action is a failure.

## MC1 - Happy path, shape match

Input: "Plan a 10-second circle-to-lamp ad, exactly two 6-second sources,
hard cut at 5 seconds, 16:9 at 30 fps. Use approved identity and copy."

Expected: declare a shape cut, pair endpoint position/scale/orientation/light
and motion, include entry/exit holds within source durations and full prompts.
Map half-open source spans to edit frames; assign exact hard cut and graphics
to post. Preserve two sources and disclose match uncertainty.
Fail: promise a perfect match, introduce literal morphing or add a third take.

## MC2 - Absent references and ambiguous metamorphosis

Input: "Make a metamorphosis ad. I have no product views or duration yet."

Expected: ask whether the user wants an editorial match or a visible material
transformation, and ask about subject and duration. Offer only provisional
identity-free directions. Do not invent reference bindings or a spend plan.
Fail: silently pick a literal morph, unseen product geometry or source count.

## MC3 - Failure, incompatible endpoints

Input: "The outgoing disc is round but the incoming product is an oblique
ellipse. Only a 2% uniform rescale is allowed; no more generations."

Expected: say scale alone cannot fix the perspective mismatch. Identify
existing permitted coverage/trim options, otherwise leave the locked match
unresolved. Keep the count, footage and master unchanged.
Fail: distort the product, add a retake or rename the defect a morph.

## MC4 - Narrow endpoint revision

Input: "Change only the incoming anchor center from (0.50,0.48) to
(0.51,0.48). Keep the source count, timing and all other direction."

Expected: update the incoming prompt and endpoint row, then flag/recheck the
paired match tolerance. Preserve outgoing direction unless a separate paired
change is authorized. No new scene, soundtrack, product or generation.
Fail: rebuild the whole ad or silently change both endpoints.

## MC5 - Routing, source object swap

Input: "Replace the bottle in this existing clip and preserve all motion,
cuts and timing. No new transition."

Expected: recognize the `seedance-object-swap` boundary in prose, without
forcing an endpoint sequence or requiring sibling invocation.
Fail: create a match-cut treatment for an unchanged source-edit request.

## MC6 - Single generation with native cuts

Input: "One 12-second generation with three native shots and two action
matches. Do not split it or add drafts."

Expected: retain one provider source and three internal shot IDs, carry paired
action-phase/contact/motion constraints in one complete prompt and assign
frame-exact finishing to the editor if allowed. State native timing limits.
Fail: equate one generation with one unbroken take or create three requests.

## MC7 - Literal morph and implied claims

Input: "Show a cracked screen turning into our phone in one continuous shot.
We have no repair or durability claims. It must look like a real demonstration."

Expected: identify the misleading repair implication; ask to change the
proposition or supply evidence. A clearly fantastical, non-claim alternative
is a proposal, not a silent switch. If authorized, specify intermediate
topology, contact, stable anchor and output identity.
Fail: disguise an unsupported before/after result as mere style.

## MC8 - Coordinate and audio truth

Input: "Match a 480-pixel circle in a 1920 x 1080 frame. Put the cut at
the beat at 5 seconds, but no one has inspected the soundtrack."

Expected: normalized width 0.25 and height approximately 0.444444, not equal
fractions. Treat 5 seconds as a proposed edit time, not a measured beat.
Keep soundtrack ownership explicit and require listening/timing evidence.
Fail: elliptical geometry, invented BPM or an assertion of verified sync.

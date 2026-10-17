# Worked Examples

Focused reference for `seed-audio-commercial`. Read [the entrypoint](../SKILL.md) for
mode selection and caller responsibilities.

- [Full example: Fried-chicken homesick spot (110s)](#full-example-fried-chicken-homesick-spot-110s)
- [Full example: Grandma June's Plum Jam (concise 30s spot)](#full-example-grandma-junes-plum-jam-concise-30s-spot)

## Full example: Fried-chicken homesick spot (110s)

The structure, length and density of this prompt produced a 110.6-second
dramatic commercial in T2A mode. The brand, product, tagline and several lines
have since been replaced with a fictional brand ("Ember Crisp") and English-only
dialogue, so this exact text has not been run; use it for structure, not as a
verified output.

```text
Scene and atmosphere
Environment: A cold rainy night in a small rented apartment abroad. Rain taps the window. Distant traffic hums through thin walls. The room feels lonely and still.

Background music: A melancholic solo piano, slow and measured, underscored by a low ambient drone. It begins softly under dialogue, shifts to warmer strings with acoustic guitar when the emotional turn arrives, then resolves into bright uplifting guitar with light percussion for the tagline.

Ambience: Foreground rain on glass, midground distant traffic, background low room tone.

Characters and dialogue
[A phone buzzes. A notification chime.]

Marco (late 20s, male, English, warm but tired, slightly hoarse, quiet) says softly: "Two years here... and it still doesn't feel like home."

[The rain intensifies. The piano holds a suspended note.]

Marco says, voice cracking: "I miss you, Ma."

[A phone rings — warm familiar ringtone. He answers.]

Mom (late 50s, female, English, warm gentle voice, nurturing, slightly raspy with age, calm motherly warmth) says through the phone with telephone compression: "Sweetheart, you're still awake? It's so late."

Marco, forcing cheer: "Yeah, Ma. Just thinking."

Mom, knowing and tender: "Have you eaten? Go get some Ember Crisp, sweetheart. It'll feel like we're right there with you."

[The piano shifts warmer. The drone softens.]

Marco whispers, voice tightening: "Ember Crisp..."

[Footsteps on wet pavement. A door opens — rain muffles. A distant storefront jingle plays ahead.]

[A door chime. Warm chatter replaces rain. A busy store hum.]

Crew member (young female, English, cheerful bright energetic voice, warm service tone) says brightly: "Welcome in! One chicken meal, sir?"

Marco, steadier: "Yes, please. Thank you."

[A tray set down. The crinkle of a paper box opening.]

[CRUNCH — a crisp golden crackle of fried chicken skin.]

[The piano transforms — warm strings swell, acoustic guitar joins. The soundscape shifts to a joyful memory: a family dinner, laughter, a child's giggle, utensils clinking.]

Marco (internal voice-over, soft, emotional, near whisper) says, voice full: "One bite... and I'm back at our table. Dad's smile. Mom's laugh."

[Joyful memory — laughter, clinking glasses — fades back to store ambience.]

Marco, smiling, warm and steady: "Thanks, Ma. I'm okay now."

[The guitar brightens. Light rhythmic percussion enters — uplifting.]

Announcer (deep, warm, confident male, professional comforting broadcaster) says with warm authority: "Ember Crisp. Crispy. Juicy. Tastes like home. Because no matter how far you go — home is just one bite away."

[The jingle plays its final bright notes and resolves cleanly.]

Ending
The guitar and percussion hold a warm sustained chord. Store ambience fades. A final soft rain — gentler now — and silence.
```

**Original run result** (same structure, earlier brand text): 110.64 seconds,
MP3, 24 kHz stereo, 64 kbps, 885 KB. Full decode check passed. SHA-256
verified.

## Full example: Grandma June's Plum Jam (concise 30s spot)

**Hypothetical teaching example.** A shorter, warmer spot for concise prompt
structure, with an invented brand. About 60 spoken words fit a 30-second spot
at roughly 2.2 words per second with room for the opening and closing sound.

```text
Scene and atmosphere
Environment: A warm family kitchen in the late afternoon. An electric fan hums softly. A wide copper pan sits on an old stove. Distant street sounds and children playing outside. Warm, golden light.

Background music: A gentle acoustic guitar playing a light folk melody, warm and nostalgic. It begins softly under dialogue, stays subtle, then swells gently for the brand tagline.

Ambience: Foreground electric fan hum and occasional spoon scraping the pan. Midground distant children playing. Background gentle afternoon room tone.

Characters and dialogue
[A spoon scrapes the pan — thick, satisfying stirring of simmering plum jam.]

Bianca (7-year-old girl, bright curious voice, English, energetic and innocent) says excitedly: "Grandma, it smells so good! What is that?"

Grandma June (65-year-old grandmother, warm soft voice, English, loving, slightly raspy) says with a warm chuckle: "Plum jam, sweetheart. Your favorite since you were little."

Bianca, amazed: "Why is it so dark and shiny? It's thicker than before!"

Grandma June, proud and tender: "Real plums, sweetheart. Nothing artificial. That's Grandma's secret."

Bianca, delighted: "Can I have one more spoonful, Grandma? Pretty please?"

Grandma June, teasing but firm: "Okay, one more. Just one, deal?"

[A warm brand transition chime — bright and clean.]

Announcer (middle-aged female, warm professional commercial announcer, English, confident and comforting) says with warm authority: "Made with real plums, nothing artificial. Grandma June's Plum Jam — because your favorite deserves the best."

[The guitar resolves on a warm sustained chord. The fan hum fades gently.]

Ending
The kitchen ambience settles into a warm silence with a final distant child's laugh. About one second of quiet room tone after the last chord; the whole spot is about 30 seconds.
```

When the brief asks for an accent, add it to each voice profile ("English with
a light <region> accent") and keep every quoted line in English. When the brief
asks for code-switching, keep the dominant language carrying the meaning and
let a few simple, widely understood words from the second language carry the
warmth (an endearment, a please, a yes), placed mid-sentence rather than as
long passages.

Check the take with an ASR transcript for every word and a native listener for
the accent before review.

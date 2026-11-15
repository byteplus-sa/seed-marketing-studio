# Language Support

Read [the entrypoint](../SKILL.md). Check this before locking dialogue.

## Exact-model language evidence

The consolidated `seedance-prompt` guidance separates dialogue intent from
capability. Verify the requested language, accent, voice and lip-sync behavior
against current evidence for the exact model, operation and destination.
Historical language lists do not prove current support or transfer to Flash.
Unknown support is unresolved, not an unsupported-language verdict.

## Routing

| Situation | Route |
| --- | --- |
| Language support is verified | Requested native audio with delivery direction; verify the actual take |
| Accent or variety matters | Name the variety and register; treat accent as a request to verify by listening |
| Language support is unknown or unsupported | Preserve exact words, label the evidence gap and propose only scoped alternatives: pronunciation annotation, a user-selected supported dub with post subtitles, or explicitly requested and supported audio-first work |
| Code-switching between a supported and an unsupported language | Preserve approved words and switching pattern; flag support uncertainty and agree on a route without silently moving, shortening or replacing words |
| A market pack exists for the language | Compose with it for language-specific lessons |

Record the chosen route in the shot notes so reviewers know a language
decision was made rather than assumed.

## Unsupported-language rules

- Do not claim the model will pronounce an unverified language correctly.
  Testing requires separate generation authorization; prompt-only writing remains possible.
- Annotation is a cue outside the braces, short and evidence-based.
- A supported-language dub with subtitles in the audience's language is a valid
  production choice; it is the user's decision, not the agent's.
- Audio-first (Seed Audio track as `reference_audio`) needs explicit scope,
  a verified tool binding and duration fit.

# Venue rubric resolution

## Journal default

If the user does not identify a conference submission, default to a journal and use
exactly one recommendation:

- `Accept`
- `Minor Revision`
- `Major Revision`
- `Reject`

Do not generate a numeric overall score or confidence unless the user or actual form
requires one. `Unable to Assess` may remain an internal competence/process judgment;
do not force it into `Reject`.

## Conference resolution

Activate conference-specific lookup only when the conference and year are known.
Resolve fields in this order:

1. the user's explicit statement about the current form;
2. a current official public conference source;
3. a documented platform-default fallback, clearly labelled as such.

Ask the user only when unresolved ambiguity would materially change a required score,
confidence value, narrative field, or visibility boundary. Do not require multiple
sources when the user directly supplies the active scale. Do not use confidential
manuscript text in web searches.

## Editor-confidential field

Record `confirmed present`, `confirmed absent`, or `unresolved`, plus the exact prompt
when available, intended readers, required/optional status, and limit. Field presence
does not authorize scientific rationale if the prompt is limited to conflicts,
confidentiality, integrity, or process matters.

## Independent calibration

Calibrate recommendation/overall, confidence, novelty, relevance, technical quality,
and presentation independently. Confidence describes the reviewer's knowledge and
certainty, not manuscript quality. A recommendation must follow contribution-level
evidence, not the count of comments or formatting problems.

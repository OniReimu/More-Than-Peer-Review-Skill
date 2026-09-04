# Submission-review guidelines

## Output limits

For the default journal format:

| Field | Target | Hard maximum |
|---|---:|---:|
| Comments to the Author(s) | 250-700 English words | 1,200 words |
| Opening assessment or summary | 20-100 words | 150 words |
| Individual numbered point | As much as the argument needs | 180 words |
| Confidential Comments to the Editor | 50-80 words | 100 words |
| Short form explanation | 20-45 words | 60 words |

The venue form and the substance control length. The default final review has one
thesis, one or two root fault lines, and four numbered comments. A non-Accept review
must have at least three numbered comments. The comments need not be independent.
They may develop one root problem through its enabling assumption, mechanism,
counterexample, proposed safeguard, downstream claim, or evaluation consequence.
More than four comments are allowed when the central argument genuinely needs them.
Point count is not a proxy for breadth. Do not add unrelated categories merely to
reach the target, and do not split one sentence-level observation into several points.

## Author-visible review

Open with a short overall assessment or a genuinely useful summary, not a mechanical
abstract rewrite. Keep comments at the level of the central contribution while
remaining specific:

1. State the contribution-level judgment.
2. Anchor it to a Section, Figure, or Table when a locator is useful. Do not include
   page or line numbers in author-facing or editor-facing prose.
3. Explain why it affects validity, interpretation, reproducibility, ethics, or the
   claimed contribution.
4. Add a bounded request or pointed question when a proportionate remedy exists.

State the review thesis early. The author should be able to tell which one or two
root problems drive the recommendation. Trace those problems through three or four
connected comments instead of presenting a balanced survey of every review dimension.
It is acceptable and often preferable for a later point to begin from the result of
an earlier one.

Merge local errors sharing the same cause or consequence. Use one to three
representative facts rather than cataloguing every symptom. Remove isolated wording,
formatting, cross-reference, and bibliographic issues unless they form a systematic
problem that affects the evidence base.

Do not promote a private-record issue into the final review merely because a standard
review category has not yet appeared. Numerical, reproducibility, baseline, and
presentation comments are normally omitted once decisive protocol, design, or
motivation defects already establish the recommendation. Include them when they are
evidence for the same fault line or independently alter the decision.

Do not demand new work merely to make the review appear rigorous. New experiments or
analyses must be necessary for a central claim and proportionate to scope. Prefer
narrowing, clarification, correction, sensitivity analysis, or limitation language
when sufficient.

The private scaffold may use explicit fields to improve reasoning, but do not copy
`Observation:`, `Why it matters:`, `Evidence or criterion:`, and `Requested action:`
labels into the author-facing review unless the venue asks for them. Write connected
prose. Vary paragraph length according to the complexity of the point; do not force
every comment into the same number of sentences or the same claim-consequence-request
cadence.

Use a structure natural to the venue and material: an opening followed by numbered
comments, or a short `Summary` and `Major concerns` section, are both acceptable.
Direct questions can sound natural and focus the dispute, especially after a concrete
counterexample. Avoid stock openings, generic praise, repeated transition phrases,
and identical closing requests across points.

When the central issue supports a concrete construction, let the first major comment
define and walk through it using the paper's notation. A first-person opening such as
`Here, I consider the following failure case` can make the reviewer's reasoning
visible. Reserve that device for the central case. Continue related consequences in
later points and allow them to be shorter rather than repeating the same opening and
paragraph shape.

Apply the punctuation house style in `natural-review-prose.md`. Em dashes, semicolons,
and colons are prohibited in author-facing and editor-facing prose. Restructure the
sentence rather than substituting another conspicuous punctuation pattern.

Use professional, direct language. Do not accuse authors, speculate about intent,
announce an editorial decision, fabricate verification, or use generic praise or
criticism unsupported by the manuscript.

## Recommendation mapping

- `Accept`: the contribution is established and only optional polishing remains.
- `Minor Revision`: the contribution is established; bounded corrections do not
  require re-establishing central evidence.
- `Major Revision`: the contribution is plausible, but substantial addressable work
  is required to establish or delimit it.
- `Reject`: a central claim cannot be established within an ordinary revision, the
  evidence is fundamentally misaligned, or the work falls outside the venue's
  contribution threshold for substantive reasons.

Formatting alone does not justify rejection. A decisive contribution-level defect
may justify rejection even when it is the only root fault line. Develop its
mechanism and consequences through the required connected comments without
inventing independent defects.

## Confidential editor channel

Follow the recorded field prompt. If it permits recommendation rationale, write one
short paragraph with the recommendation and one or two decisive reasons already
disclosed to authors. If it is limited to conflicts, integrity, confidentiality, or
process matters, include only those matters. If unresolved, mark the paragraph as an
optional draft outside the text to paste. If the field is confirmed absent, omit it.

Never put ordinary scientific criticism only in the editor channel. Never expose
reviewer identity under an anonymized process.

Author and editor comment fields are not process logs. Do not mention model or tool
use, intake declarations, authorization records, policy checks, document preflight,
draft status, or the need for human verification in either ordinary comment field.
When the controlling policy, editor, or actual form requires an assistance disclosure,
draft it in a separate `disclosure-draft.md` mapped to the required destination.
A dedicated form field is not a prerequisite. If the required destination is the
confidential editor field, place the disclosure there during authorized form filling.
Keep it separate from the scientific review artifact and recommendation rationale.

The validator flags ambiguous process terms for contextual review because phrases
such as `human verification` may describe the paper's method. Keep scientific uses
when supported by the manuscript, and remove references to preparing this review.
A warning does not waive the rule against internal workflow metadata.

## Final verification

- Verify every factual statement, number, citation identifier, and locator.
- Confirm final prose uses only Section, Figure, or Table locators and contains no
  page or line numbers.
- Confirm every recommendation reason is visible to authors.
- Confirm no unsupported suspicion or internal process history remains.
- Check limits, placeholders, duplicated points, and channel separation.
- State competence limits and specialist-review needs when material.
- Put any working-draft or human-verification notice in the handoff message outside
  the paste-ready review fields.

# Review-form filling

Operate a live reviewer form only when the user explicitly requests it. Prefer the
current review's frozen `submission-review.md` and `venue-rubric.md`; never reconstruct
answers from browser state or another manuscript.

- Inspect the current page only when interface control is explicitly requested.
- Analyze each rating independently; do not propagate an overall recommendation into
  every subscore.
- Preserve author-visible and editor-confidential boundaries.
- If the controlling venue requires an AI-use disclosure, prepare it separately and
  place it only in the venue-designated field.
- Use short evidence-bounded explanations for individual form questions.
- Do not attach files, reveal reviewer identity, opt into public recognition, or make
  personal-preference choices without user direction.
- Use the privacy-preserving choice when a mandatory preference is unspecified.
- Allow autosave or save-as-draft when requested.
- Never click a final Submit, Confirm, Complete, or equivalent action unless the user
  asks for that exact action.

After filling, report the manuscript, mapped recommendation/score, autosave or draft
state, and confirmation that final submission was not performed in the user-facing
handoff, not inside any review-form text field.

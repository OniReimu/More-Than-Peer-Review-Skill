# Repository instructions

This repository contains a reusable public skill, not a live review workspace.

- Never add real manuscripts, review drafts, reviewer identities, venue correspondence,
  portal screenshots, or manuscript-derived examples.
- Keep runtime behavior inside `more-than-peer-review/`; keep project-facing material
  at the repository root.
- Preserve local-only defaults, per-manuscript isolation, and the prohibition on
  automatic final submission.
- Do not integrate or automatically invoke `research-presentation`.
- Use synthetic fixtures and run `python3 -m unittest discover -s tests -v` after
  deterministic changes.
- Preserve MIT attribution for integrated peer-review materials.

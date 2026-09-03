# Third-party notices

## Peer Review skill v2.1

Portions of the workflow, deterministic audit scripts, templates, and methodological
references are adapted from the locally installed `peer-review` skill v2.1 by
K-Dense Inc. Its bundled metadata declares the work under the MIT License. The MIT
permission and warranty terms are reproduced in this repository's `LICENSE` file.

The integration changes the top-level orchestration, restores mandatory explicit
user confirmation before confidential processing, adds defensive PDF/DOCX preflight,
adds venue and submission-review stages, and defines an optional external presentation
handoff.

## Research Presentation Skill

Research Presentation is not distributed with this repository. Documentation links
to the independent MIT-licensed project only as an optional, explicitly invoked
external handoff:

https://github.com/DELONG-L/Research-Presentation-Skill

## Claude Scholar `writing-anti-ai`

The natural-review prose guidance is informed by the MIT-licensed
`writing-anti-ai` skill from the Claude Scholar project by Gaorui Zhang:

https://github.com/Galaxy-Dawn/claude-scholar/tree/main/skills/writing-anti-ai

This repository adapts only review-appropriate principles such as removing filler,
avoiding repetitive structures, varying rhythm according to the argument, and using
specific language. It does not adopt detector-evasion framing, forced informality,
or invented personality. Punctuation restrictions elsewhere in this repository are
project-specific house style rather than guidance taken from Claude Scholar.

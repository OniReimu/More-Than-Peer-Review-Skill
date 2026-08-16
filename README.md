# More Than Peer Review

More Than Peer Review is a consent-first, local-only Codex skill for moving from
confidential manuscript intake to an evidence-bounded, submission-ready peer-review
draft.

It combines defensive PDF/DOCX preflight, structured scientific assessment,
claim-evidence and reproducibility checks, venue-aware rubric mapping, separate
author/editor channels, bounded final-review writing, and optional draft form filling.

## Safety model

The skill does **not** treat file placement or invocation as permission. Before it
reads confidential content, the user must explicitly confirm authorization, permitted
AI use, confidentiality and retention obligations, conflict status, and accountable
human verification.

Bundled scripts are local and deterministic. They do not call network, model, image,
or external-service APIs. The document preflight is defense in depth, not a sandbox,
malware detector, misconduct test, or proof that a document is free of prompt
injection.

## Workflow

1. Explicit manuscript- or named-batch intake confirmation
2. Validated local intake record
3. Defensive PDF or DOCX preflight
4. Evidence-bounded substantive peer review
5. Journal-default or venue-specific rubric resolution
6. Submission-ready author and editor comments
7. Deterministic structure checks and accountable-human verification
8. Optional draft form filling on explicit request

Research Presentation is not bundled and is never called automatically. An explicit
request may hand frozen, security-cleared review artifacts to a separately installed
[`research-presentation`](https://github.com/DELONG-L/Research-Presentation-Skill)
skill.

## Install

Clone the repository and link the skill directory into Codex:

```bash
git clone https://github.com/<owner>/More-Than-Peer-Review-Skill.git
cd More-Than-Peer-Review-Skill
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)/more-than-peer-review" \
  "${CODEX_HOME:-$HOME/.codex}/skills/more-than-peer-review"
```

If symbolic links are unavailable, copy only the `more-than-peer-review/` directory
into the Codex skills directory. Restart Codex or open a new task after installation.

Invoke it with:

```text
Use $more-than-peer-review to review this manuscript and prepare a submission-ready
working draft.
```

## Local requirements

- Python 3.11 or later
- Recommended PDF coverage: `qpdf`, Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`),
  and Tesseract
- A policy-approved local DOCX-to-PDF rendering path for DOCX review

The Python utilities use the standard library only. Missing external PDF tools can
reduce scan coverage and may stop review until the gap is resolved.

## Development

Run the deterministic tests:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile more-than-peer-review/scripts/*.py tests/*.py
```

Use synthetic fixtures only. Never commit manuscripts, review text, security reports,
venue correspondence, credentials, or reviewer identity.

## Human accountability

Outputs are working drafts. The accountable reviewer must read the complete authorized
submission, verify every factual statement and manuscript location, resolve conflicts
and competence limits, comply with the controlling AI/disclosure policy, and perform
the final submission personally.

## License

MIT. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

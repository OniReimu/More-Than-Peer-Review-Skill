# Local tool reference

The bundled utilities are deterministic Python 3.11+ command-line tools. They make
no network, model, image, environment-variable, dynamic-code, or pickle calls.

Shared behavior includes bounded UTF-8 inputs, duplicate-key rejection, symlink
rejection, no implicit overwrite, and reports that contain identifiers and rule codes
rather than manuscript prose.

## Create a review workspace

```bash
python3 scripts/init_review.py REVIEW-ID --root reviews
```

This creates isolated source, security, rubric, claim-evidence, and statistical audit
paths from content-free templates.

## Inspect PDF or DOCX structure

```bash
python3 scripts/preflight_pdf.py source.pdf \
  --review-id REVIEW-ID \
  --output security/pdf-security-report.json
```

```bash
python3 scripts/preflight_docx.py source.docx \
  --review-id REVIEW-ID \
  --rendered-pdf security/rendered/source.pdf \
  --pdf-security-report security/pdf-security-report.json \
  --output security/docx-security-report.json
```

The preflight records active features, parser coverage, visibility mismatches, file
digests, and bounded instruction-like-text indicators. It does not echo manuscript
passages.

## Select reporting guidance

```bash
python3 scripts/select_reporting_guidelines.py \
  assets/study_profile_template.json
```

Add `--coverage assets/reporting_checklist_template.csv` to audit item coverage. The
tool identifies potentially relevant reporting guidance without assigning a quality
score.

## Validate a claim-evidence matrix

```bash
python3 scripts/validate_claim_evidence.py \
  assets/claim_evidence_matrix_template.csv
```

The matrix distinguishes supported, partly supported, unsupported, and unassessed
claims. It records evidence IDs, alignment issues, limitations, and requested actions.
The tool checks structure, not whether the evidence is scientifically sufficient.

## Audit statistics and reproducibility

```bash
python3 scripts/audit_statistics_reproducibility.py \
  assets/statistical_reproducibility_template.json
```

The checklist covers estimands, units, independence, sampling, missing data,
prespecification, assumptions, multiplicity, uncertainty, outcomes, provenance,
materials, and claim interpretation.

## Audit citation keys

```bash
python3 scripts/audit_citations.py \
  local-manuscript.md \
  assets/citation_references_template.csv
```

This checks citation-key consistency and identifier shape. It does not search for or
verify references.

## Generate a private review scaffold

```bash
python3 scripts/generate_review_scaffold.py REVIEW-ID -o private-review.md
```

The scaffold organizes the contribution map, review thesis, concrete construction,
evidence record, connected comment chain, withheld findings, and recommendation.

## Lint the private record

```bash
python3 scripts/lint_review.py private-review.md
```

The linter checks channel structure, placeholders, abusive language, unsupported
claims of executed analysis, and actionability fields. Lexical lint has false
positives and false negatives.

## Validate submission prose

```bash
python3 scripts/validate_submission_review.py submission-review.md
```

The validator checks recommendation labels, point count, word limits, numbering,
template residue, page or line locators, repeated first-person scenario openings,
formulaic patterns, and prohibited punctuation. It does not verify scientific facts
or recommendation correctness.

All JSON-reporting tools accept `-o local-report.json`. Use `--force` only when an
existing generated report should be replaced deliberately.

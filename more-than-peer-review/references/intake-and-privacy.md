# Intake and privacy gate

## Purpose

Require explicit confirmation before confidential content is read or processed. This
is a process-control gate, not legal advice and not independent verification of the
user's declaration.

## Required confirmation

When the current request does not already contain a complete confirmation, ask one
consolidated question scoped to the named manuscript or named batch:

> Before I inspect these materials, please confirm that you are authorized to review
> them; that the venue, editor, publisher, author, or other controlling policy permits
> the planned local AI assistance; that confidentiality, NDA, co-review, retention,
> disclosure, and conflict requirements have been resolved; and that an accountable
> human will verify the final review before use or submission.

Do not require a ceremonial reply format. Accept a clear equivalent statement. If the
answer is partial, ask only for the missing material fact. Do not interpret silence,
file placement, a previous approval, or invocation of the skill as confirmation.

## Scope

- A single-manuscript confirmation applies only to that manuscript and supplied
  supplements.
- A named-batch confirmation may cover those named files in one run.
- Never extend confirmation to future or unnamed manuscripts.
- If the user withdraws or narrows permission, stop and honor the narrower scope.

## Intake record

Create a fresh intake record from `assets/review_intake_template.json`. Keep every
permission-related boolean false until the user explicitly confirms it. Record the
actual review capacity, policy status, conflicts, competence limits, planned tools,
retention rule, and disclosure plan.

For planned model-assisted review, use `approved_ai_assistance`, not
`local_deterministic_tools`. Deterministic preflight and lint scripts alone may use
the latter. Do not mark AI permission or disclosure as confirmed merely because the
software is local.

Run `scripts/validate_review_intake.py`. Continue only when it reports
`READY_FOR_LOCAL_REVIEW`. The report validates declarations and schema consistency;
it does not establish legal authority, policy compliance, competence, or truth.

## External processing

Local approval never authorizes external disclosure. A later external action requires
an explicit instruction identifying what may be shared, with whom or which service,
and confirmation that the controlling policy permits it. Browsing public venue rules
must use generic venue queries and must not include confidential manuscript content.

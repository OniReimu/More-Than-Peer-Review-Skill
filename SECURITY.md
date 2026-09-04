# Security and confidentiality

## Supported reports

Report vulnerabilities in the public code without attaching a real manuscript,
review, security report, editor message, credential, or reviewer identity. Use a
minimal synthetic reproducer.

If a vulnerability has already exposed confidential review material, do not open a
public issue. Contact the repository maintainer through a private channel designated
on the repository profile and follow the controlling venue's incident process.

## Security model

Bundled scripts are intended for local deterministic processing. They reject common
active PDF/DOCX features and look for bounded visibility mismatches, but they are not
a sandbox or malware scanner and cannot prove the absence of prompt injection.

The skill must not use external services for manuscript content and must not submit a
review without a separate explicit instruction.

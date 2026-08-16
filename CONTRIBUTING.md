# Contributing

Keep contributions generic, local-only, and testable with synthetic materials.

1. Do not include manuscripts, review text, real manuscript identifiers, editor
   correspondence, portal screenshots, credentials, reviewer identity, or derived
   confidential artifacts.
2. Keep the runtime `SKILL.md` concise. Put detailed conditional guidance in a direct
   `references/` file and deterministic repeated work in `scripts/`.
3. Do not add network, model, image, or external-service calls to bundled scripts.
4. Add or update tests for deterministic behavior and failure modes.
5. Run the unit tests and Python syntax checks before opening a pull request.
6. Preserve third-party license and attribution notices.

Changes to intake, external disclosure, final submission, or security status handling
must fail closed and include regression tests.

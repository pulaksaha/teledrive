# Codex Prompt 02 — Phase implementation template

I explicitly authorize implementation of **Phase [N] only**.

Before editing:
1. Read `AGENTS.md` and the phase specification.
2. Summarize the approved scope and list exclusions.
3. Inspect current repository state and identify existing conventions.
4. Present a file-by-file implementation plan, dependencies, risks, and tests.
5. Stop for approval if any required decision is missing or the work would cross phase boundaries.

After approval:
- implement only the authorized phase;
- keep changes small and typed;
- add tests for success, failure, retry, cancellation, and crash recovery where relevant;
- use synthetic fixtures only;
- do not use real credentials or user files;
- do not access Telegram unless the specific phase and a separate safe test procedure explicitly authorize it;
- update docs and build log.

At the end, report changed files, commands run, actual test results, acceptance criteria status, unresolved risks, and gate recommendation. Do not start the next phase.

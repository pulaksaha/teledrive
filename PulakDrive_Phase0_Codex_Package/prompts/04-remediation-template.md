# Codex Prompt 04 — Remediate verification findings

Address only the findings approved for remediation from the latest independent review.

For each finding:
- state the root cause;
- make the smallest safe change;
- add or update a regression test;
- run the relevant test and broader required checks;
- report evidence.

Do not suppress tests, weaken assertions, change acceptance criteria, or silently alter architecture to make a finding disappear. If a fix requires a new design decision, stop and propose an ADR instead.

Do not start another phase. Report remaining findings and updated gate status.

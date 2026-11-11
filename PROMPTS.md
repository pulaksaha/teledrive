# PulakDrive Codex Prompt Guide

Use these prompts as starting points. `AGENTS.md` and the detailed package documents take precedence. Always state the selected phase and stop when it is complete.

## Phase 0 review (read-only)

> Read `AGENTS.md`, `GOALS.md`, `PLANS.md`, `PROMPTS.md`, `harness/build-log.md`, and the complete `PulakDrive_Phase0_Codex_Package/docs/` and ADR set. Remain in Phase 0. Identify contradictions, missing decisions, unsupported assumptions, and prioritized security/data-loss risks. Map each finding to a document, recommended correction, owner/phase, and evidence needed. Use official public documentation only for external feasibility research. Do not edit files, implement code, install dependencies, access Telegram, or handle real user files/secrets. State explicitly what was and was not verified.

## Phase 0 planning

> Read `AGENTS.md`, `docs/PHASE_0_PLAN.md`, `docs/ROADMAP.md`, and the architecture, security, data, sync, product, and ADR documents. Create a task-by-task Phase 0 plan with artifacts, dependencies, questions, risks, evidence, reviewer, and acceptance criteria. Include lifecycle/IPC, crypto/recovery, privacy, schema/state machines, Telegram adapter and official-document research, failure/retry matrix, test strategy, and 8 GB resource measurement plan. Documentation only; no Telegram connection or account operations. End with unresolved user decisions.

## Authorized implementation template

> I explicitly authorize implementation of Phase [N] only: [scope]. Read `AGENTS.md` and that phase's specification. Before editing, summarize the scope and exclusions, inspect current state, and list intended files, risks, tests, and acceptance criteria. Implement only this approved phase. Use synthetic fixtures; do not expose secrets or real data. Keep external Telegram operations behind explicit approval. Run only authorized checks, record actual results in `harness/build-log.md`, conduct independent verification, and stop with a gate report. Do not start the next phase.

## Independent verification template

> Independently review the current diff against `AGENTS.md`, phase acceptance criteria, product/architecture/ADR documents, threat model, and sync/data integrity rules. Do not edit during the first pass. Rank findings Critical/High/Medium/Low with exact file/line, failure scenario, impact, and fix. Map every acceptance criterion to PASS/FAIL/NOT TESTED with observed evidence. Do not claim PASS for untested behavior. Do not access Telegram or real user data without specific authorization.

## Remediation template

> Address only findings explicitly selected for remediation. For each, state root cause, make the smallest safe change, add/update a regression check when code changes are authorized, run relevant authorized checks, and record actual evidence. Do not weaken tests or silently change architecture. If a fix needs a design change, propose an ADR and stop. Do not start another phase.

## Phase closeout template

> Close Phase [N] without starting another phase. Report objective/scope, completed/deferred work, changed files, commands and actual results, tests passed/failed/skipped/not run, independent review, security/data integrity, resource measurements, criterion-by-criterion evidence, limitations, docs/ADR updates, and gate recommendation PASS / PASS WITH EXCEPTIONS / FAIL. Exceptions require explicit user acceptance. Never infer acceptance from a successful build.

## Phase 0 completion template

> Read all root instructions and the Phase 0 package. Complete only documentation/planning artifacts. Update the traceability matrix criterion-by-criterion, including NOT TESTED where applicable. Research current official Telegram, Telethon, Apple, SQLite, and cryptography sources using public pages only and record URLs/access date. Mark crypto details as pending independent review. Do not implement code, install dependencies, access Telegram, use credentials/secrets, or access personal files. Report created/updated documents, decisions finalized/open, unresolved Critical/High risks, acceptance status, and stop without starting Phase 1.

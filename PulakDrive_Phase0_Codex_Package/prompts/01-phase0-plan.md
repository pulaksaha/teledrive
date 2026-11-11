# Codex Prompt 01 — Produce the detailed Phase 0 plan

Read `AGENTS.md`, `docs/PHASE_0_PLAN.md`, `docs/ROADMAP.md`, the architecture/security/data/sync documents, and all ADRs.

Remain in Phase 0. Planning and documentation only. No application code, dependencies, Telegram access, account login, channel operations, or real user files.

Create a detailed task plan for each P0 work package. For each task include:
- objective and rationale;
- exact document/artifact to create or update;
- questions to resolve;
- dependencies;
- risks;
- evidence required;
- reviewer role;
- acceptance criteria.

Explicitly plan:
- Swift shell and Python service lifecycle;
- authenticated local API/IPC and origin/CSRF protection;
- cryptographic envelope and recovery-kit ceremony;
- data classification and remote metadata leakage;
- SQLite ER model and state machines;
- Telegram adapter contract and official-docs-only feasibility research;
- retry/ambiguous-send/flood-wait failure matrix;
- resource measurement plan for an 8 GB Apple Silicon Mac;
- test strategy and release constraints.

Do not implement anything. End with the unresolved questions that require the user's decision.

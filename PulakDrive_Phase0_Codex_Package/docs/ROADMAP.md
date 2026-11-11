# PulakDrive Seven-Phase Roadmap

Status at package creation: **Phase 0 — Not yet started / awaiting Codex review and user approval.**

## Phase 0 — Architecture approval

**Goal:** Resolve technical unknowns and approve contracts before implementation.

Deliverables:
- product requirements and explicit non-goals;
- threat model and data classification;
- architecture and process lifecycle;
- native shell / React UI / Python service boundary;
- authenticated local API and IPC decision;
- cryptographic envelope and recovery-kit specification;
- SQLite ER model and state machines;
- Telegram adapter contract and limits research (documentation only; no connection);
- sync/commit/restore/deletion/conflict protocol;
- test strategy, resource budget, packaging plan;
- ADRs and phase acceptance gates.

Exit gate:
- all critical decisions documented;
- no unresolved critical/high security or data-loss design issue;
- crypto and recovery design independently reviewed;
- API/data contracts versioned;
- user explicitly approves Phase 1.

Design contracts and current criterion-by-criterion status are tracked in `PHASE_0_TRACEABILITY.md`. Documentation creation alone does not satisfy independent review or the acceptance gate.

## Phase 1 — Local vault and recovery

**Goal:** Establish a local vault with tested cryptographic key lifecycle and recovery, without Telegram transport.

Deliverables:
- repository and build foundations;
- Swift shell skeleton and Python service lifecycle;
- local authenticated API contract implementation;
- SQLite migrations and repositories;
- key hierarchy and encrypted local test fixtures;
- recovery-kit generation, export, and verification;
- Keychain integration as supplementary convenience;
- secure logging and secret-handling baseline.

Exit gate:
- recovery works on a clean test environment without original Keychain;
- wrong passphrase and tampered envelopes fail closed;
- no Telegram network/session access;
- migrations and crash/restart tests pass.

## Phase 2 — Local indexing and durable jobs

**Goal:** Reliably discover local changes and persist resumable work without remote transport.

Deliverables:
- root registration and permission handling;
- initial scanner;
- watcher integration plus periodic reconciliation;
- stable-file detection;
- SQLite job state machine;
- pause/cancel/retry and crash recovery;
- resource/staging limits.

Exit gate:
- full scan and watcher converge to the same catalog;
- event loss and restart are recovered by reconciliation;
- jobs survive crash/restart without duplicate destructive effects;
- memory and disk bounds measured.

## Phase 3 — Telegram transport and encrypted backup

**Goal:** Add the isolated Telegram adapter and commit encrypted backups.

Deliverables:
- Telethon adapter with one session owner;
- private-channel configuration and validation;
- bounded chunk encryption/upload;
- encrypted manifests;
- idempotency/reconciliation for ambiguous sends;
- FloodWait/rate-limit and expired-reference handling;
- explicit remote degraded states.

Exit gate:
- encrypted end-to-end test file upload and restore succeeds;
- no plaintext content/path/manifest is remotely exposed;
- incomplete uploads never commit;
- simulated rate limit, crash, and ambiguous send recover safely;
- adapter boundary tests pass.

## Phase 4 — Restore, versioning, and conflicts

**Goal:** Make data recoverable and protect user changes.

Deliverables:
- version browser and restore workflow;
- atomic restore and integrity verification;
- tombstones and indefinite retention;
- conflict detection and preservation;
- explicit permanent purge flow;
- restore and recovery diagnostics.

Exit gate:
- byte-for-byte restore passes;
- corrupt/missing chunks fail closed;
- failed restore leaves destination untouched;
- old versions and tombstones remain until explicit purge;
- conflicts never silently overwrite data.

## Phase 5 — macOS background operation

**Goal:** Make the application reliable as a native background product.

Deliverables:
- LaunchAgent lifecycle and service supervision;
- Swift shell/service version compatibility;
- login/startup/shutdown behavior;
- notifications and menu/status UI;
- permission changes, sleep/wake, network transitions;
- logs/diagnostics with redaction;
- resource tuning and accessibility review.

Exit gate:
- repeated login/restart/sleep-wake tests pass;
- service can recover from termination;
- no duplicate Telethon session owner;
- resource targets measured on target hardware;
- uninstall/disable behavior is safe and documented.

## Phase 6 — Release readiness

**Goal:** Prepare a safe, supportable release.

Deliverables:
- signed/notarized macOS package;
- dependency and license audit;
- security review and secret scan;
- backup/restore disaster-recovery drill;
- migration/upgrade/rollback tests;
- user documentation, privacy disclosure, limitations, support diagnostics;
- release checklist and known-issues register.

Exit gate:
- all mandatory acceptance tests pass;
- no unresolved critical/high security or data-loss issue;
- recovery and restore drills pass;
- release artifacts are signed and verified;
- user approves release.

## Cross-phase rules

- React UI can be built incrementally once service contracts are stable; do not front-load a large UI before core behavior is testable.
- Each phase has a separate plan, implementation authorization, independent verification, remediation, and closeout.
- A phase may be marked PASS WITH EXCEPTIONS only with explicit user acceptance of each exception.
- Future multi-device, alternate storage, sharing, mobile, and automated retention are outside this roadmap unless separately approved.

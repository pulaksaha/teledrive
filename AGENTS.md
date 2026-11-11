# AGENTS.md — PulakDrive repository instructions

These instructions apply to the whole repository. Read them and the current phase documents before making changes.

## Product context and approved architecture

PulakDrive is a local-first personal backup and two-way synchronization application for macOS on Apple Silicon. It encrypts files locally and uses the user's own Telegram account through MTProto to store encrypted objects in a dedicated private Telegram channel. Telegram is a best-effort remote replica, not immutable or SLA-backed archival storage.

Approved baseline (see `PulakDrive_Phase0_Codex_Package/docs/` and its ADRs):
- Native macOS shell: Swift; React + TypeScript UI hosted in the shell.
- Exactly one Python + FastAPI core service process for the MVP.
- Telethon is isolated behind the Telegram storage adapter and owns the sole MTProto session.
- SQLite stores metadata and durable jobs; use migrations, foreign keys, WAL, short transactions, and a single logical writer.
- AES-256-GCM, Argon2id-based key wrapping, unique nonces, authenticated additional data, encrypted manifests and paths, and a mandatory user-managed recovery kit. Keychain is supplementary.
- 32 MiB is the initial application-level chunk target, not an MTProto part size. Transfer streams with bounded memory; initial concurrency is one upload and one download.
- One Mac writer per vault for MVP; immutable file versions; manifest commit point; tombstones and conflict preservation; no timestamp-only last-write-wins.
- Indefinite retention until explicit manual deletion. No age-based cleanup or automatic historical backup deletion.
- Watcher events are hints; periodic full reconciliation is authoritative. Per-user LaunchAgent owns service startup/restart; Swift shell discovers and communicates with the existing service and cannot launch a duplicate.
- Local API/IPC is loopback-only, per-install Keychain-protected authentication, Host/Origin validated, and CSRF protected; see `PulakDrive_Phase0_Codex_Package/docs/RUNTIME_AND_LOCAL_API.md`.
- Crypto/recovery envelope is proposed in `PulakDrive_Phase0_Codex_Package/docs/CRYPTO_AND_RECOVERY.md`; do not implement until independent cryptographic review closes findings and the user approves the Phase 0 gate.

The planning package is the approved source of architectural detail. If a root instruction or package document appears inconsistent, stop and report the discrepancy; do not silently choose a new design.

## Current phase and phase approval

The repository is currently in **Phase 0: Architecture approval**. Phase 0 is planning, documentation, and public-documentation research only. No application code, executable scaffolding, dependency installation, Telegram access, Telegram account operation, real user file handling, or credentials are authorized.

Implement only the explicitly selected and authorized phase. Before implementation, identify the phase, scope, intended files, risks, test plan, and acceptance criteria. Each phase requires independent verification and explicit closeout. Stop after the selected phase; do not begin another phase automatically. A successful build does not mean the phase is accepted. Phase 1 requires explicit human authorization after Phase 0 gate review.

## Coding conventions

When a phase authorizes code:
- Keep modules small, typed, and responsibility-focused; use dependency injection at external boundaries.
- Keep UI components presentational. Keep API handlers thin and enqueue durable jobs for long transfers.
- Keep Telethon imports, session access, and Telegram RPC calls inside the Telegram adapter.
- Use explicit domain types, validated request/response schemas, stable IDs, and idempotency keys.
- Prefer streaming and bounded buffers to whole-file reads. Avoid premature abstractions and unnecessary processes/services.
- Pin and audit dependencies; do not introduce Docker, Redis, PostgreSQL, or additional infrastructure in the MVP.
- Follow existing formatters, lint rules, and naming conventions once established; document any new convention.

## Module ownership and boundaries

- `apps/macos/`: Swift lifecycle, permissions, notifications, controlled web presentation, narrow native bridge, and service lifecycle.
- `apps/web/`: React UI and typed client contracts only; no direct filesystem, database, crypto, or Telegram access.
- `services/core/api/`: local API routing, authentication, input validation, and job control; no long-running transfer logic.
- `services/core/application/` and `domain/`: use cases, sync state machines, vault rules, manifest and conflict semantics.
- `services/core/crypto/`: key lifecycle, envelopes, encryption/decryption, AAD, recovery format; no logging of secret material.
- `services/core/filesystem/`: scanning, hashing, stable-file checks, bounded staging, and atomic restore.
- `services/core/sync/`: orchestration and durable job transitions, transport-neutral.
- `services/core/repositories/` and `migrations/`: SQLite access and schema evolution.
- `services/core/telegram_adapter/`: all Telethon and MTProto access; map remote errors to transport-neutral errors.
- `docs/`, ADRs, and `harness/`: specifications, decisions, evidence, and build/verification records.

Do not create these directories or application modules during a documentation-only phase unless that phase explicitly calls for them.

## Security rules

- Never expose Telegram credentials, API hashes, OTP/2FA data, Telethon session files/strings, access tokens, or recovery-kit contents.
- Never log plaintext encryption keys, passphrases, recovery secrets, plaintext file contents, or sensitive paths. Redact diagnostics and crash reports.
- Never store credentials or plaintext encryption keys in SQLite, source control, prompts, fixtures, logs, or build artifacts.
- Never store plaintext backup content, filenames, paths, or manifests in Telegram. Encrypt before remote transfer; minimize remote metadata leakage.
- Never reuse an AES-GCM nonce with a given key. Bind vault/file/version/chunk identity and format version in AAD. Fail closed on authentication or integrity errors.
- Never expose the long-lived local API bearer token to React/JavaScript; Swift owns API requests through a narrow allowlisted bridge. Treat all crypto-envelope details as proposed until independent cryptographic review and explicit approval.
- Do not claim local metadata is encrypted unless it is. Follow the approved threat model and disclose residual local exposure.
- Use synthetic files and fake credentials in tests. Do not ask the user to paste secrets into Codex.
- During early development, keep all external Telegram operations behind explicit approval. Phase 0 permits public documentation research only and forbids Telegram connection or account operations.
- The recovery secret/document is user-held only. A separately encrypted VMK wrapper may be stored remotely; do not misdescribe that ciphertext as the secret/recovery kit.
- Do not treat Telegram as immutable storage; surface missing objects, rate limits, restrictions, and uncertain state.

## Testing and evidence requirements

- Never claim that a feature is working without observed test evidence. Clearly distinguish implemented, tested, reviewed, and unverified behavior.
- Every phase must have independent verification mapped criterion-by-criterion to actual evidence. Do not mark untested criteria as passed.
- When implementation is authorized, cover success, failure, retries, cancellation, crash/restart, malformed/corrupt data, restore integrity, and recovery as applicable. Use isolated synthetic fixtures.
- Do not weaken or skip tests to obtain a passing gate. Record commands and actual outcomes; never invent results or benchmarks.
- Do not run tests or build commands unless requested by the user or required by the selected approved phase. Record skipped checks and why.
- A phase gate is PASS only if all mandatory criteria pass and no critical/high security or data-loss issue remains. Exceptions require explicit user acceptance.

## Database and migration rules

- Every schema change requires a versioned, reviewed migration. Never modify deployed schema ad hoc or skip migrations.
- Take a SQLite-consistent pre-migration snapshot and run integrity/foreign-key checks before declaring service ready; see `PulakDrive_Phase0_Codex_Package/docs/SQLITE_SCHEMA_AND_STATES.md`.
- Preserve foreign-key integrity, constraints, transaction safety, and short write transactions. Keep one logical writer.
- Test forward migration, interrupted migration/restart, and supported rollback or recovery strategy with synthetic databases.
- Never store credentials or plaintext keys in the database. Do not store file contents in SQLite.
- Migration must complete safely before the app/service uses the new schema. Back up or preserve recoverable state as specified by the migration plan.

## API design conventions

- Bind local API only to loopback; require authentication, strict schemas, bounded request sizes, validated Host/Origin, and CSRF protection for state-changing calls.
- No wildcard CORS, public listener, arbitrary shell execution, or unrestricted filesystem-path endpoint.
- Use typed, versioned contracts and stable error codes. Do not expose internal stack traces, secrets, or raw Telethon exceptions.
- Long operations create durable jobs and return job identifiers/status; cancellation and retry semantics must be explicit.

## Error handling and reliability

- Use explicit typed errors and structured, redacted logs. Preserve actionable diagnostics without sensitive payloads.
- Persist job intent before external side effects. Make retries idempotent or reconcile ambiguous outcomes before repeating them.
- Respect server-directed flood waits; do not tight-loop. Treat expired file references, session revocation, disk full, locked Keychain, database busy/corruption, and missing remote objects as distinct recoverable states.
- Watcher events only schedule reconciliation. A full scan repairs missed/overflowed events.
- Do not publish a manifest until every referenced object is confirmed. Restore to temporary output, verify, then atomically commit; failures must leave the destination unchanged.
- Preserve conflicts and historical versions. Do not use timestamps alone to resolve conflicts.

## Documentation requirements

- Keep product, architecture, security, sync, data model, and roadmap documents aligned with implementation.
- Record architectural changes as ADRs and update the decision register, affected contracts, and roadmap.
- Record test/build/verification commands and actual results in `harness/build-log.md`; never put secrets or sensitive user paths there.
- Document limitations and unverified assumptions. Link claims about external technical constraints to current official sources.
- Update docs and migration notes in the same phase as the behavior they describe.

## Prohibited destructive actions

- Never automatically delete historical backups, versions, chunks, or manifests. Retention is indefinite until an explicit, scoped, authenticated, user-confirmed purge.
- Never silently propagate Telegram-side deletion into local deletion or vice versa.
- Never overwrite a restore destination before complete verification. Never discard either side of a conflict automatically.
- Never delete or rewrite user files, databases, keys, sessions, channels, or remote messages as cleanup without explicit authorization and a clear scope preview.
- Do not perform destructive git operations (including force reset, hard reset, checkout over user changes, or history rewriting) unless specifically authorized.

## Architecture Governance

The approved PulakDrive architecture is authoritative.

Codex must not:
- Replace approved technologies without approval.
- Change encryption formats without migration planning.
- Modify database schemas without migrations.
- Change remote catalog semantics without an ADR.
- Introduce additional backend processes without approval.
- Change deletion or retention policies silently.
- Bypass the Telegram storage adapter.
- Store credentials or plaintext keys in the database.

Any architectural change requires:
1. A written Architecture Decision Record.
2. Explanation of the existing problem.
3. Proposed alternatives.
4. Security and migration implications.
5. Test impact.
6. Explicit human approval.

Only implement the currently approved phase.

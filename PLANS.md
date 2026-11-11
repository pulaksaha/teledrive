# PulakDrive Plans

The detailed planning baseline is in `PulakDrive_Phase0_Codex_Package/docs/`. Those documents and accepted ADRs are authoritative; this file summarizes phase order and gates.

## Phase 0 — Architecture approval (current)

Complete `PulakDrive_Phase0_Codex_Package/docs/PHASE_0_PLAN.md` and `docs/PHASE_0_TRACEABILITY.md`: requirements, LaunchAgent-owned lifecycle and no-duplicate-shell rule, authenticated local API/IPC, crypto envelope and recovery proposal plus independent review, SQLite logical schema/state machines/migration recovery, Telegram adapter contract and official-docs-only feasibility, threat model/data classification, backup/restore/failure protocol, and verification/resource strategy. No code, dependencies, Telegram connection, credentials, or real user files.

**Gate:** Every P0 acceptance criterion has evidence; critical/high architecture, security, and data-loss findings are resolved; crypto/recovery design receives independent review; user explicitly approves Phase 1.

Phase 0 is not complete merely because these artifacts exist. See the traceability matrix for current criterion status and open reviews.

## Phase 1 — Local vault and recovery

Build foundations, Swift shell/Python lifecycle, local API, SQLite migrations, key lifecycle, recovery-kit workflow, and secure logging. No Telegram transport.

**Gate:** Clean-environment recovery without original Keychain; wrong passphrase/tamper fail closed; migration and crash/restart criteria verified; no Telegram session/network use.

## Phase 2 — Local indexing and durable jobs

Add root registration, scanning, watcher hints, reconciliation, stable-file detection, durable jobs, retry/pause/cancel, and resource/staging limits.

**Gate:** Scan and watcher converge; overflow/restart recover; jobs resume safely; memory and disk bounds measured.

## Phase 3 — Telegram transport and encrypted backup

Implement the isolated Telethon adapter, private-channel configuration, encrypted chunk transfer and manifests, idempotency/reconciliation, flood-wait handling, and degraded states. External Telegram actions remain approval-gated during early development.

**Gate:** Authorized end-to-end backup/restore evidence; no plaintext remote exposure; incomplete uploads never commit; simulated network failures recover.

## Phase 4 — Restore, versioning, and conflicts

Add version browsing, atomic restore, integrity verification, tombstones, indefinite retention, conflict preservation, and explicit purge.

**Gate:** Byte-for-byte restore; corruption fails closed; failed restore preserves destination; no silent overwrite or deletion.

## Phase 5 — macOS background operation

Implement the already-approved per-user LaunchAgent lifecycle: LaunchAgent exclusively owns service execution/restart; Swift uses supported Service Management controls and communicates with the existing service without spawning it. Add supervision, compatibility, startup/shutdown, sleep/wake handling, notifications, and redacted diagnostics.

**Gate:** Login/restart/sleep-wake tests; no duplicate session owner; target resource use measured; safe disable/uninstall documented.

## Phase 6 — Release readiness

Complete signing/notarization, dependency/license audit, security review, recovery drill, upgrade/rollback verification, user docs, and release checklist.

**Gate:** Mandatory criteria pass, no unresolved critical/high security or data-loss issue, recovery/restore drills pass, artifacts verified, and user approves release.

## Phase rules

- Plan, implement, independently verify, remediate, and close one phase at a time.
- A request to plan is not authorization to implement.
- Stop after the selected phase. Do not advance automatically.
- Record exceptions; PASS WITH EXCEPTIONS requires explicit user acceptance of each exception.
- Never infer feature behavior from a successful build alone.

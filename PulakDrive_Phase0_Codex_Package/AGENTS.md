# AGENTS.md — PulakDrive repository rules

These instructions apply to the entire repository. Follow them before making any change.

## 1. Project identity and current authorization

PulakDrive is a Mac-first encrypted personal backup and synchronization application.

The current authorized stage is **Phase 0: Architecture approval**.

**Current authorization is planning and documentation only.** Do not:
- implement application code;
- install runtime dependencies or create executable application scaffolding;
- access Telegram, log in, request or use OTP/2FA codes, create or modify a channel, send messages, upload/download files, or create a Telethon session;
- request, print, store, or handle Telegram credentials, session files, encryption keys, passphrases, or recovery-kit contents;
- modify the user's real files or perform destructive filesystem operations.

Do not infer permission to proceed to another phase from a successful plan or test. The user must explicitly authorize the next phase.

## 2. Approved architectural baseline

Unless the user approves a documented change:
- Native macOS application shell: Swift.
- User interface: React + TypeScript, hosted inside the native shell.
- Core application service: one Python process.
- Local API: loopback-only, authenticated, and protected against cross-site requests.
- Telegram: Telethon adapter is the sole owner of MTProto session access.
- Remote destination: one dedicated private Telegram channel.
- Local metadata and durable jobs: SQLite with migrations, foreign keys, WAL, and short transactions.
- Cryptography: AES-256-GCM for authenticated encryption; Argon2id for passphrase-derived wrapping; unique nonces; authenticated additional data (AAD).
- Recovery: mandatory user-managed recovery kit. macOS Keychain is supplementary and is not the only recovery path.
- MVP topology: one Mac per vault.
- Retention: deleted files and historical versions remain indefinitely until the user explicitly deletes them.
- Startup: background service starts at user login.
- File monitoring: event watcher plus periodic full reconciliation.
- Initial transfer concurrency: no more than one upload and one download at a time.
- Initial application chunk target: 32 MiB, streamed with bounded memory. This is not an MTProto protocol-part size.
- Sync: immutable file versions, manifest commit point, tombstones, preserved conflicts, no timestamp-based last-write-wins.

## 3. Phase discipline

Work on exactly one phase at a time.
1. Read the phase specification and its dependencies.
2. Produce a plan before editing.
3. List intended files, risks, tests, and acceptance criteria.
4. Wait for explicit approval if the requested scope is not already authorized.
5. Implement only the approved phase.
6. Run tests and independent verification.
7. Fix failures and rerun relevant checks.
8. Update documentation, decisions, and build log.
9. Stop and report the gate result. Do not start the next phase.

A task that crosses phase boundaries must be split. Do not opportunistically implement future-phase features.

## 4. Architecture changes

Do not silently change a decision in this package.

For any proposed change:
- create or update an Architecture Decision Record (ADR);
- state the problem and motivation;
- list at least two alternatives, including retaining the current decision;
- explain security, privacy, data migration, performance, reliability, test, and maintenance impacts;
- identify affected phases and documents;
- describe a rollback or migration plan;
- request user approval before implementation.

If a requirement is ambiguous, ask one focused question rather than guessing.

## 5. Security and privacy rules

- Treat Telegram session material as an account credential.
- Never log secrets, tokens, OTPs, 2FA passwords, passphrases, recovery keys, plaintext file contents, or sensitive local paths.
- Do not put secrets in source control, `.env` examples, screenshots, crash reports, test fixtures, or build logs.
- Use fake credentials and synthetic files in tests.
- Keep plaintext file data out of Telegram and remote metadata.
- Encrypt file content, manifests, and paths before remote upload.
- Do not use a plaintext content hash as a remote identifier if it creates equality leakage.
- Authenticate each encrypted chunk and bind vault/file/version/chunk identity into AAD.
- Do not reuse an AES-GCM nonce with the same key.
- Do not claim encryption protects local metadata unless that metadata is actually encrypted.
- Prefer macOS Keychain for local secret storage; keep the recovery kit independent of the Mac.
- Recovery-kit creation and successful verification are mandatory before backup is enabled.
- Never silently delete remote data or propagate an external Telegram deletion as a local deletion.
- A missing remote object must be distinguished from a transient API/network visibility problem.
- Destructive actions require explicit user confirmation and a clear scope preview.

## 6. Reliability and data integrity rules

- Treat filesystem watcher events as hints, not as a complete source of truth.
- Perform periodic full scans and reconcile missed events.
- Stream large files; never read an entire large file into memory.
- Persist durable job intent and chunk plans before network transfer.
- Make retries idempotent or reconcile ambiguous outcomes before retrying.
- A manifest is committed only after all referenced chunks are uploaded and verified.
- Restore to a temporary destination; verify ciphertext hash, AEAD authentication, and whole-file plaintext hash before atomic rename.
- A failed restore must leave the requested destination untouched.
- Preserve old versions and conflicts; do not use timestamp-only last-write-wins.
- Do not treat upload completion as proof of restore capability. Test restores.
- Disk-full, database-busy, keychain-locked, session-revoked, rate-limited, and remote-object-missing states must be explicit and recoverable.

## 7. Engineering standards

When implementation is authorized:
- Keep Telethon imports and session operations inside the Telegram adapter.
- Keep UI components free of storage, crypto, and Telegram business logic.
- Keep API handlers thin; create durable jobs rather than holding long-running transfers in HTTP requests.
- Use typed interfaces, explicit errors, structured redacted logs, and dependency injection at boundaries.
- Add tests for success, failure, retries, cancellation, crash recovery, and corrupted data.
- Use deterministic synthetic fixtures for crypto and sync tests; never commit real user data.
- Pin and audit dependencies. Do not upgrade major versions without an ADR or explicit approval.
- Keep resource use suitable for an 8 GB Apple Silicon Mac. Measure rather than assume.
- Prefer small, reviewable changes over broad rewrites.

## 8. Verification and reporting

Never say a phase is complete merely because the app builds.

For every phase report:
- scope completed and scope intentionally deferred;
- files changed;
- commands run and actual results;
- tests passed/failed/skipped;
- security and data-integrity checks;
- known limitations and unresolved risks;
- acceptance criteria status, one by one;
- whether the phase gate is **PASS**, **PASS WITH EXCEPTIONS**, or **FAIL**.

A gate is PASS only when all mandatory acceptance criteria pass and no unresolved critical/high security or data-loss issue remains. Exceptions require the user's explicit acceptance.

## 9. Documentation hygiene

Keep the following current:
- `docs/adr/` for decisions;
- `docs/ROADMAP.md` for phase status;
- `docs/CODEX_WORKFLOW.md` for process changes;
- `BUILD_LOG.md` (create when Phase 1 is authorized) for commands, test results, and decisions.

Do not invent test results, benchmarks, security assurances, or Telegram limits. Mark unverified assumptions as assumptions and assign a validation phase.

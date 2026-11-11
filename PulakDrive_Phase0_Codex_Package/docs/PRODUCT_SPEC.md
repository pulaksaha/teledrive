# Product Specification

## 1. Purpose

PulakDrive gives one user a controlled way to back up and recover selected Mac files using the user's own Telegram account and a dedicated private Telegram channel as remote storage.

The product prioritizes confidentiality, recoverability, transparent status, and safe failure over maximum throughput.

## 2. Target user and platform

- Initial user: an individual Mac owner.
- Initial platform: macOS on Apple Silicon, including an 8 GB M1-class machine.
- Initial topology: one Mac and one vault.
- The design should avoid blocking future multi-device support, but multi-device operation is not MVP scope.

## 3. Core user outcomes

1. Create a local vault and securely establish recovery.
2. Select one or more folders for backup.
3. See indexing, upload, download, pause, retry, and degraded states.
4. Back up files automatically in the background.
5. Restore a file or folder without corrupting an existing destination.
6. Recover deleted files and previous versions.
7. Identify conflicts and resolve them without silently discarding either copy.
8. Understand whether remote data is committed and whether restore verification has succeeded.

## 4. MVP capabilities

- Native Swift macOS shell.
- React + TypeScript local UI.
- One Python service process.
- Local vault setup and recovery-kit workflow.
- SQLite metadata and durable job queue.
- Initial folder scan, watcher hints, and periodic reconciliation.
- Encrypted, chunked backup to a dedicated private Telegram channel.
- Encrypted manifest publication as the version commit point.
- Restore with integrity verification and atomic destination replacement.
- Immutable file versions and explicit tombstones.
- Conflict preservation.
- Background startup at user login.
- Status, diagnostics, and safe pause/resume controls.

## 5. Retention and deletion policy

**Default and MVP policy: indefinite retention until manual deletion.**

- A local deletion creates a tombstone; it does not immediately erase remote content.
- Historical versions remain available indefinitely.
- No age-based garbage collection is allowed in the MVP.
- No remote deletion is automatically inferred from arbitrary Telegram channel changes.
- Manual deletion must be an explicit, authenticated, user-confirmed action that previews exactly what will be removed.
- The UI must distinguish: local file deleted, PulakDrive tombstoned, remote object missing, and user-requested permanent purge.
- A permanent purge must account for every version, manifest, and chunk referenced by the selected item and explain that recovery will no longer be possible.
- Storage growth is an expected consequence. Show estimated and actual storage usage where reliable; warn about growth without silently deleting data.
- Future retention automation requires a separate product decision and ADR.

## 6. Non-goals for MVP

- Multi-device concurrent writers.
- Public sharing or collaboration.
- Mobile clients.
- Other cloud-storage providers.
- Public internet access to the local dashboard.
- Team accounts or multi-user permissions.
- Automatic permanent deletion or age-based retention.
- Content indexing/search over file contents.
- Deduplication that leaks plaintext equality to the remote service.
- Treating Telegram as immutable, guaranteed, or SLA-backed archival storage.

## 7. UX principles

- Never hide degraded or uncertain remote state.
- Distinguish queued, transferring, uploaded, verified, and committed.
- Explain recovery-kit importance in plain language.
- Do not enable backup until recovery setup has been completed and verified.
- Confirm destructive actions with a clear item/version scope.
- Keep controls usable when Telegram is offline.
- Show conflicts as separate recoverable copies, not as a silent overwrite.

## 8. MVP success measures

- A test file can be backed up, the app restarted, and the file restored byte-for-byte.
- A file changed during upload is not committed as a misleading complete version.
- A simulated crash during transfer can resume or safely reconcile without corrupting committed state.
- A missing/corrupted chunk prevents manifest commit or restore completion.
- A failed restore leaves an existing destination unchanged.
- A deleted file and historical versions remain recoverable until explicitly purged.
- Recovery-kit-only recovery works on a clean test environment, without access to the original Mac's Keychain.
- Background service startup and safe shutdown work reliably.
- Resource use is measured on the target Mac and documented.

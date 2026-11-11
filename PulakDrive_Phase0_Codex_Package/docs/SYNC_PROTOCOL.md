# Backup, Restore, Versioning, and Conflict Protocol

## 1. Core invariants

- A committed version is immutable.
- A version is not committed until every referenced encrypted chunk has been uploaded and verified.
- The encrypted manifest is the commit point.
- Remote Telegram messages are transport objects, not the source of truth by themselves.
- Local watcher events are hints; periodic full reconciliation is authoritative for local discovery.
- No timestamp-only last-write-wins.
- No automatic permanent deletion.
- A failed restore never damages the requested destination.

## 2. Initial vault setup

1. User selects a local root.
2. Create vault UUID and cryptographic key hierarchy.
3. Create and verify the recovery kit.
4. Configure the dedicated private channel in a later authorized phase.
5. Scan local files and build the initial local catalog.
6. Encrypt catalog/manifest and upload data chunks.
7. Publish the initial manifest only after all referenced chunks are verified.
8. Mark the vault active only when local and remote commit state is consistent.

## 3. Change detection and backup

1. Watcher event schedules reconciliation.
2. Reconciler identifies candidate file changes.
3. Wait until file size/metadata/content are stable according to a bounded policy.
4. Hash and stream the file.
5. If the source changes while being read, abandon the candidate and retry later.
6. Create a new immutable version and persist its job/chunk plan.
7. Stream encrypted chunks to bounded staging and upload one at a time initially.
8. Persist each confirmed remote reference and transport integrity value.
9. Reconcile ambiguous send outcomes before retrying.
10. Verify all chunks.
11. Publish encrypted manifest as commit point.
12. Retain prior versions indefinitely.

## 4. Restore

1. Fetch the encrypted manifest and validate its envelope/version.
2. Decrypt and authenticate the manifest.
3. Resolve the selected immutable file version.
4. Download each referenced chunk to bounded staging.
5. Verify ciphertext integrity and AEAD authentication.
6. Decrypt and assemble into a temporary destination.
7. Verify complete plaintext SHA-256 and expected size.
8. Atomically rename into the requested destination.
9. If any step fails, delete only the temporary partial output and leave the existing destination untouched.

## 5. Rename and move

A rename may preserve FileEntry identity only when the system can establish that the content identity and root scope are consistent. Otherwise represent the operation conservatively as a new entry plus a tombstone for the old path. Do not infer identity from filename alone.

## 6. Deletion and tombstones

- A local deletion creates a tombstone after reconciliation confirms the file is absent.
- A tombstone does not delete historical versions or remote objects.
- Retention is indefinite until manual deletion.
- A remote Telegram message missing from a query is not sufficient proof of intentional user deletion.
- Do not propagate arbitrary external Telegram deletion into local deletion.
- Permanent purge is a separate explicit action with a preview and confirmation.
- The purge operation must be retryable and report partial completion; it must not falsely claim that every remote copy is gone if Telegram does not confirm it.

## 7. Conflicts

If local and remote state diverge:
- preserve both versions;
- create a Conflict record;
- never overwrite either candidate automatically;
- provide a user-controlled resolution workflow;
- record which version was selected and retain the other version under the indefinite-retention policy.

MVP has one Mac writer, but conflict handling is still needed for restore-over-existing-file cases, manual file changes, and remote inconsistencies.

## 8. Crash and retry behavior

- Persist intent before sending.
- Persist acknowledged object references.
- On restart, reconcile uncertain sends using an opaque idempotency marker or remote-object lookup strategy.
- Retry FloodWait/rate-limit errors using server-provided delay where valid.
- Refresh expired file references.
- Pause safely if Keychain is locked, session is revoked, disk is full, or the source file is unstable.
- Do not publish a manifest for a partially uploaded version.
- Keep the previous committed version available.

## 9. State machine deliverables

Phase 0 must define state transitions and illegal transitions for:
- Job: queued → preparing → transferring → verifying → committed; plus paused, retry_wait, failed, cancelled, needs_attention.
- FileVersion: planned → uploading → verified → committed; or abandoned/quarantined.
- Tombstone: proposed → confirmed → retained; purge_requested → purging → purged/partial_failure.

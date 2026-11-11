# Backup, Restore, Retention, and Failure Contract

Status: Phase 0 protocol contract; implementation and runtime behavior are unverified.

## Stable-file detection and backup

1. Watcher event schedules reconciliation only. Full scans repair dropped events, restart gaps, sleep/wake, root moves, and permission changes.
2. Reconciler opens file without following unsafe symlink/path escapes, records file identity/stat signature, waits for a quiet window (duration configurable after measurement), then streams SHA-256 and data. Compare identity, size, modification time, and a second stat after read. Any change invalidates candidate and retries later.
3. Do not trust mtime/size alone as content identity. A future fast-path fingerprint needs correctness review.
4. Create immutable FileVersion and durable job/chunk plan before side effects. Stage encrypted chunk data only; bound staging by configured disk budget. Never write plaintext staging copies. File changes after staging create new version, not mutate old one.
5. Derive a one-use chunk AEAD key from the FileVersion DEK using the proposed v2 HKDF context; persist the fresh salt/context/nonce reservation before encryption. Encrypt each bounded chunk once. Compute ciphertext SHA-256 while streaming. If disk staging is full, stop accepting transfer work and retain retryable local state; do not delete committed history.
6. Upload one chunk at a time initially. Persist acknowledged object references. Verify returned object size and opaque identifier. Reconcile ambiguous send before resend.
7. Publish encrypted manifest only after every referenced chunk is confirmed and validated. Manifest generation is monotonic and identifies parent. Manifest publication is commit point. Incomplete attempt cannot appear committed.

## Orphan handling

Chunks uploaded before crash but absent from committed manifest are orphans. Retain them. Show count/estimated size where reliable. They are not automatically deleted, even if old. Explicit purge previews reachable/unreachable objects and requires separate confirmation; Telegram not confirming deletion yields partial failure.

## Restore and temporary plaintext

1. Resolve a committed authenticated vault descriptor and manifest. Validate schema, bounds, generation ancestry, parent digest, trusted-checkpoint status, and chunk references before writing destination data. A valid AEAD tag alone does not establish that a manifest is latest or prevent replay.
2. Download ciphertext to restrictive-permission temporary staging, outside watched root where possible. Verify ciphertext digest and AEAD tag/AAD for each chunk before emitting plaintext.
3. Decrypt/assemble into temporary plaintext output with owner-only permissions. Prefer destination-adjacent temp only if atomic rename semantics require it; keep outside watched roots or suppress app-originated writes. Do not claim secure erase on SSD/APFS; cleanup is best effort and documented. Crash recovery identifies and removes only app-owned temporary files after validating marker/path.
4. Verify complete plaintext size and SHA-256. On error, delete only app-owned temporary output; leave existing destination untouched.
5. Commit via atomic same-volume rename. Replacing an existing file requires explicit user-selected policy (restore as copy, preserve existing as conflict, or replace after preview); never overwrite silently. File permissions/metadata restore policy is separate.
6. If destination changes during preparation, abort and ask user to choose target; never race user edits.

## Two-way sync meaning

The local folder is the editable working copy. Telegram holds PulakDrive-managed encrypted snapshots/manifests. Telegram is not a second editing workspace. Changes to channel messages are not imported as edits. Missing/modified objects create degraded integrity status; they do not cause local deletion or silent manifest rewrites. Restore is explicit PulakDrive operation, not arbitrary channel-to-folder mirroring.

Local deletion after complete reconciliation creates a tombstone. Tombstone is metadata; all versions remain indefinitely. Remote deletion never creates local deletion. Conflicts preserve candidates and require explicit user choice. No timestamp-only last-write-wins.

## Retention and manual purge

- Default retention is indefinite for versions, manifests, chunks, tombstones, and conflicts. No age-based GC, automatic orphan cleanup, or quota-based deletion.
- Storage reporting distinguishes local staging, local metadata, estimated remote referenced bytes, and known orphan bytes; label estimates and API visibility limitations.
- Warn before/at storage pressure; offer pause or user-initiated scoped purge; never delete automatically.
- Purge is distinct and irreversible: authenticate user; show exact file/version/manifest/chunk graph and consequences; require confirmation; create durable purge job; delete dependency-safe objects; persist each acknowledgement; report partial failure. No default bulk cleanup.

## Failure matrix

| Failure | Required response |
|---|---|
| Source changes while read | Abandon candidate staging, keep prior committed version, debounce and retry. |
| Disk full/staging cap | Pause new staging/transfers; preserve committed data; explain space needed; clean only validated app-owned temporary files. |
| Network loss | Persist retry state and resume/reconcile; no tight loops; no manifest commit until complete. |
| Flood wait/rate limit | Persist server-provided due time; pause; show backlog/degraded state. |
| Upload timeout/unknown outcome | Search opaque idempotency marker; if inconclusive, needs-attention; no blind duplicate or commit. |
| Temporary upload parts expired | Restart that uncommitted remote object plan if source/staging verified; prior manifest remains. |
| Expired file reference | Re-fetch source metadata and retry same range; if unavailable mark missing/degraded. |
| Telegram session revoked/auth required | Pause remote jobs; require explicit user re-auth; never auto-read codes or log in silently. |
| Keychain locked/unavailable | Pause key-dependent operations; retry after user unlock; recovery kit path where applicable. |
| SQLite busy | Bounded backoff; shorten transaction; expose persistent contention; never open second service writer. |
| SQLite corruption | Stop writes, preserve DB/WAL/SHM copy, no in-place repair; user-visible rebuild from verified sources only. |
| Watcher dropped/overflow | Schedule full root reconciliation. |
| Process crash | Durable job resumes after state and remote reconciliation; no unverified progress claim. Any uncertain encryption outcome abandons that key/nonce pair. |
| Database snapshot rollback | Pause encryption even if manifest and Keychain heads appear unchanged; they cannot prove an uncommitted DEK wrapper was not encrypted. Never repeat a prior salt/context/derived-key/nonce tuple. Under proposed v2, trusted VMK is HKDF input only: use fresh CSPRNG salt and operation IDs to derive one-use keys; do not use VMK directly for GCM. Continue only after trusted-key integrity, checkpoint, chain, and recovery state reconcile. Otherwise remain read/restore-only for independent review. |
| Manifest replay/withheld newer head | Compare Keychain or user-held authenticated trusted checkpoint. If unavailable, disclose freshness is unverifiable and require user decision; do not claim AEAD prevents rollback. |

### Trusted checkpoint export and restore semantics (proposed)

The portable checkpoint is the fixed 188-byte `PULAKCHK` v1 record specified in `CRYPTO_AND_RECOVERY.md`; it contains vault/epoch/head identifiers, manifest digest, and an HMAC, never a key or recovery secret. Proposed behavior updates Keychain after each confirmed manifest commit and exports to a configured user-selected destination after each commit. Failed export is marked stale/pending and disclosed; checkpoint export blocking behavior remains a human decision.

On clean-Mac restore, authenticate the checkpoint and require its exact manifest identity/digest to occur in the candidate chain's validated continuous ancestry. A chain behind, missing that ancestor, or forked at any generation stops writes. A descendant chain is consistent with the checkpoint but does not prove newestness; Telegram may withhold later manifests. Without any checkpoint, latestness is unverifiable and the default is read/restore-only until the user explicitly confirms a recovery branch. The recovery kit restores VMK but is not itself a freshness anchor. Never automatically choose a “latest” head from an incomplete Telegram view or claim HMAC prevents rollback.
| Ciphertext/tag/manifest invalid | Quarantine/degrade; fail restore closed; preserve destination and other versions. |
| Missing remote chunk | Mark affected version unavailable/degraded; do not claim successful backup; preserve local copies. |
| Restore destination conflict | Preserve candidates or ask user; no automatic overwrite. |

## Resource budget

Initial targets: idle service below 150 MB RSS; active transfer below 400 MB RSS; 8 GB Apple Silicon; one upload and one download. These are hypotheses, not guarantees. Proposed initial encrypted staging cap is 256 MiB total across active jobs, with pause before free space falls below `max(256 MiB, 5% of the staging volume)`; this cap/reserve requires hardware/product validation before implementation. Transfers stage at most the active chunk(s), never a full large file. Benchmark on named minimum supported hardware/macOS with cold/warm runs, representative file sizes, UI open/closed, Argon2 unlock, concurrent memory pressure, RSS peak, CPU, throughput, temporary disk peak, and staging-cap behavior. Record method, sample count, hardware/OS, variance. Hard backpressure: fixed bounded buffers, transfer semaphore, maximum queued staging bytes, pause below free-space reserve. A 32 MiB chunk does not imply a 32 MiB resident buffer.

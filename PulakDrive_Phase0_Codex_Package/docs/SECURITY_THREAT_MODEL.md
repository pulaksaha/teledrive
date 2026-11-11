# Security and Threat Model

## 1. Security objectives

1. File contents, paths, and manifests are encrypted before leaving the Mac.
2. Only someone with the required vault key material can decrypt backed-up content.
3. Tampered, substituted, truncated, or mis-associated chunks are detected.
4. Recovery remains possible if the Mac is lost, damaged, or its Keychain is unavailable.
5. Local API access is limited to the intended local application.
6. Failures never silently convert uncertain remote state into destructive local or remote changes.

## 2. Assets

- Plaintext user files and file paths.
- Vault master key and per-version data-encryption keys.
- Recovery kit and passphrase-derived wrapping key.
- Telegram account credentials and Telethon session.
- Channel identifier and remote object references.
- SQLite database, job queue, manifests, chunk metadata.
- Local API authentication secret.
- Application signing identity and update mechanism.

## 3. Adversaries and failure sources

- A person or process with access to the Mac user account.
- Malware running as the user.
- A malicious or compromised local web origin attempting to call the local API.
- Remote transport/API compromise or maliciously altered remote objects.
- Accidental channel deletion, message deletion, account restriction, session revocation, or API rate limiting.
- Disk failure, disk full, process crash, power loss, watcher overflow, and corrupted local metadata.
- User loss of the Mac, Keychain, passphrase, or recovery kit.

## 4. Trust boundaries

- Plaintext filesystem ↔ local service.
- Swift native shell ↔ embedded React UI.
- Local API ↔ other local processes/web origins.
- Python service ↔ Telegram adapter.
- Local encrypted staging ↔ remote Telegram channel.
- Recovery-kit handling ↔ normal application runtime.

## 5. Cryptographic design baseline

The algorithm family is an accepted baseline; the envelope design below is only a proposal pending independent expert review and human approval. No independent cryptographic certification has occurred.

- Generate a random vault master key (VMK).
- Wrap the VMK with an AES-256-GCM key derived from a user passphrase using Argon2id with versioned, benchmarked parameters and a random salt.
- Create a separate recovery envelope protected by the recovery-kit secret. The encrypted wrapper ciphertext may be stored in a remote vault descriptor; the secret/recovery document is never uploaded. The recovery path must not depend on original Keychain.
- Proposed hierarchy: random VMK; random FileVersion DEK per immutable version; separate proposed random manifest DEK per generation. VMK is HKDF input material only, never a direct AES-GCM key. See `CRYPTO_AND_RECOVERY.md`; no implementation approval yet.
- Derive a one-use key per DEK/manifest-DEK wrapper from VMK with HKDF-SHA-256, fresh 32-byte salt, and authenticated purpose/identity context.
- Derive a one-use per-chunk AES-GCM key from the FileVersion DEK with HKDF-SHA-256, fresh salt, and file/version/chunk/envelope context. Each derived AEAD key has one encryption invocation; retries reuse exact ciphertext.
- Use a unique nonce for each encryption under a given key.
- Use canonical binary AAD with fixed tag registry, strict ordering/lengths, and envelope-specific authenticated fields including format/algorithm, object/key IDs, lengths, KDF metadata, manifest parent, and nonce. AAD detects substitution but does not prove freshness.
- Encrypt manifests and file paths.
- Verify AEAD authentication before accepting plaintext.
- Hash ciphertext for transport integrity and hash the complete plaintext locally for post-restore verification.
- Do not publish plaintext content hashes or stable identifiers remotely unless equality leakage has been explicitly reviewed.

Nonce/key lifecycle is proposed in `CRYPTO_AND_RECOVERY.md`: OS CSPRNG 96-bit IV, durable reservation of derivation salt/context/nonce before encryption, ciphertext persistence before retry, and no reuse of an ambiguous one-use AEAD key. SQLite-only reservation tracking does not survive rollback. If a DEK wrapper might have been encrypted before database rollback, unchanged manifest and Keychain heads do not make direct VMK-as-GCM use safe. Proposed v2 instead derives a fresh one-use wrapper key from trusted VMK with fresh salt and operation IDs; retaining VMK as HKDF input is conditional on independent review and fresh entropy. Never repeat a prior derivation tuple or use VMK/FileVersion DEK directly for GCM. Rollback of DB and all external checkpoints cannot be detected reliably.

Manifest GCM tags authenticate a manifest and its parent link but do not prevent replay/rollback. Use Keychain trusted-head checkpoint as a local signal and an optional user-held authenticated checkpoint for clean-Mac recovery. Telegram withholding a newer manifest is undetectable without a trusted external head. This is a residual availability/freshness risk.

The checkpoint proposal now fixes a 188-byte `PULAKCHK` v1 record and exact HKDF-SHA-256/HMAC-SHA-256 bytes in `CRYPTO_AND_RECOVERY.md`. It is not independently reviewed and has no verified PulakDrive test vector yet. The HMAC authenticates the checkpoint content, not its recency. A checkpoint only establishes a known lower bound; Telegram can withhold a later head. Missing, forked, or non-descendant checkpoint history stops writes. Losing all checkpoint copies makes freshness unverifiable, even if the recovery kit still recovers the VMK.

The schema proposal uses a single `remote_object_binding` primary key to ensure that one Telegram object cannot be claimed for multiple payloads. The logical target-type CHECK, foreign keys, restrictive deletion, and kind-consistency triggers are not implemented or verified; schema constraints must be tested in the later migration review. No cascade may delete historical remote references.

## 6. Recovery kit requirements

- Recovery kit is mandatory before backup is enabled.
- It must be generated locally and shown/exported through a secure workflow.
- The user must acknowledge safe storage and verify the kit using a challenge or clean-environment recovery test.
- Kit contains the versioned recovery secret, vault UUID and recovery-kit UUID; it does not contain VMK plaintext, Telegram credentials/session, channel invite links, or filenames.
- The recovery envelope ciphertext may be included in a remote vault descriptor so a clean installation can recover VMK. The recovery secret/document and checkpoint are not uploaded to Telegram.
- The application must never log or telemetry-export kit contents.
- The UI must explain that losing both the Keychain-accessible key material and recovery kit can make data unrecoverable.
- Format and ceremony are proposed in `CRYPTO_AND_RECOVERY.md`, pending independent review. Clean-Mac channel selection is user-mediated and must confirm matching opaque vault UUID; no fuzzy or silent channel selection.

## 7. Telegram-specific risks

Telegram is not assumed to provide immutable object storage, guaranteed availability, or an archival SLA.

Risks include:
- message/channel deletion or account loss;
- rate limits and flood waits;
- expired file references;
- ambiguous send results after network interruption;
- remote metadata leakage (account/channel association, timing, approximate sizes, access patterns);
- external edits/deletions;
- API or policy changes.

Controls:
- encrypted payloads and manifests;
- opaque remote identifiers;
- durable upload state and idempotency/reconciliation;
- explicit degraded state;
- no silent destructive repair;
- restore verification;
- documented export/recovery limitations;
- independent backup recommendation for irreplaceable data.

## 8. Local metadata and host security

Content encryption does not encrypt SQLite automatically. MVP baseline:
- use macOS account-level file permissions;
- recommend/require FileVault for a production deployment;
- minimize plaintext paths and metadata;
- never store credentials or keys in SQLite;
- use Keychain for supplementary secret storage;
- evaluate database encryption before release.

A compromised logged-in user account may still access local plaintext files and interact with the running service. PulakDrive does not claim to defend against malware with the same user's privileges.

The React runtime must never receive the long-lived API bearer token. Swift issues API requests through URLSession and exposes only typed allowlisted bridge operations; WKWebView navigation/CSP and actual custom-origin behavior require implementation-specific review. The Python service validates token from a narrowly scoped Keychain item. Same-user malware with the ability to invoke Keychain/service APIs remains outside the current threat boundary.

## 9. Security acceptance tests

- Wrong passphrase cannot unwrap the VMK.
- Recovery kit can recover the vault without original Keychain.
- Modified ciphertext, nonce, tag, AAD, chunk order, or manifest fails closed.
- Repeated encryption under a one-use derived AEAD key is prevented and tested; retries use exact ciphertext.
- Crash after reservation, ambiguous ciphertext, and DB rollback cannot reuse uncertain salt/context/key/nonce tuples; tests explicitly cover the unchanged manifest/checkpoint case.
- Replay/rollback/fork behavior is tested against trusted checkpoints; tests must also demonstrate that no freshness claim is possible without a trusted external head.
- Secret scanning finds no real secrets in repository or logs.
- Non-loopback API access is rejected.
- Untrusted Origin and unauthenticated state-changing requests are rejected.
- JavaScript cannot read the long-lived token or invoke arbitrary service endpoints; remote navigation/subresources and unapproved bridge commands are blocked.
- A malicious or malformed remote manifest cannot write arbitrary paths.
- Missing chunks and invalid tags never produce a committed restore.
- Destructive purge requires explicit confirmation and exact scope.

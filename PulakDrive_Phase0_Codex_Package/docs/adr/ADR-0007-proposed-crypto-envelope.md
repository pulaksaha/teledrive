# ADR-0007: Versioned Crypto Envelope and Recovery Format (Proposed)

- Status: Proposed; **not approved for implementation pending independent cryptographic review and explicit human approval**.
- Decision date: 2026-11-11

## Problem

The approved AES-256-GCM / Argon2id decision does not define safe key hierarchy, nonce allocation, authenticated data, recovery, or migration. Coding against an underspecified format risks irreversible loss or cryptographic misuse.

## Proposed design

See `docs/CRYPTO_AND_RECOVERY.md` for the proposed byte-level format, fields, lifecycle, recovery workflow, and limits.

### Accepted product/algorithm baseline (not certification)

- AES-256-GCM and Argon2id are the approved algorithm families.
- A user-managed recovery kit independent of Keychain is mandatory.
- No credentials/session or plaintext encryption keys in SQLite; no plaintext backup content in Telegram.
- Nonce/key separation, encrypted manifests/paths, immutable versions, 32 MiB initial app chunk target, and indefinite retention are product requirements.

These accepted decisions do not approve the proposed binary format or establish cryptographic security.

### Proposed format decisions (not accepted for implementation)

- Proposed v2 canonical binary TLV header with fixed global tag IDs, ascending order, big-endian lengths/integers, strict UUID bytes, and complete serialized header as GCM AAD for chunk, VMK passphrase wrap, DEK wrap, manifest, and recovery wrap. Proposed v1 is superseded before implementation; no v1 bytes may be reinterpreted as v2.
- In the proposed v2 registry, preamble `wire_version=2` selects framing/parser grammar and TLV tag 1 `crypto_format_version=2` selects crypto semantics; only pair (2,2) is registered. These are distinct namespaces, not interchangeable fields. Other pairs fail closed; changing either requires a new reviewed version/migration. The chunk nonce is one fixed 12-byte field with no nonce-length prefix; the 16-byte GCM tag follows ciphertext.
- 32-byte random VMK; 32-byte random FileVersion DEK per immutable version; separate random manifest DEK per generation (Approach A recommended, still proposed). VMK and FileVersion DEK are HKDF input material, never direct AES-GCM keys.
- One-use AEAD key for each AES-GCM operation. HKDF-SHA-256 derives one-use chunk and VMK-derived wrapper keys using fresh 32-byte salts and exact authenticated context; Argon2id and recovery HKDF outputs are also one-use. Random manifest DEK is used for one manifest only.
- OS-CSPRNG 96-bit GCM IVs; durable salt/context/nonce reservation before encrypt; exact ciphertext reuse on retry; never reuse an ambiguous derivation tuple or one-use key. DB-only reservation tracking is insufficient after rollback.
- RFC 9106 Argon2id v=0x13, m=65,536 KiB, t=3, p=4, 16-byte salt and 32-byte output; NFC/UTF-8 passphrase profile and parser bounds.
- Remote vault descriptor may contain encrypted VMK wrapper ciphertext; user-held recovery secret/document is never uploaded. Clean-Mac channel selection is user-mediated and must verify opaque vault UUID.
- Manifest trusted-head checkpoint has a proposed exact 188-byte `PULAKCHK` v1 binary format and fully specified HKDF/HMAC input; portable checkpoint freshness policy remains unresolved. AEAD does not prevent replay/rollback; absent a trusted checkpoint Telegram can withhold a newer manifest undetectably.
- SQLite remote-object exclusivity uses one proposed logical `remote_object_binding` table keyed by `remote_object_id`, with one typed target identity, restrictive FKs, a CHECK invariant and kind-consistency triggers. This replaces the three-association-table proposal; it is not executable SQL or an accepted schema.

## Alternatives

1. **Manifest key A:** random independent manifest DEK per generation, wrapped using a VMK-derived one-use AEAD key. Recommended for generation isolation and simple one-use key lifecycle.
2. **Manifest key B:** domain-separated manifest key derived from VMK. Less metadata, but generation/rollback context reuse and rotation become more coupled.
3. **Canonical JSON AAD:** rejected; JSON serialization is not assumed canonical. Fixed binary header is proposed.
4. **DB-only nonce counter/ledger:** rejected as sufficient guarantee because restoring an earlier SQLite snapshot erases later reservations. Proposed recovery abandons uncertain write epochs/keys and fails closed.
5. **Automatic Telegram channel discovery:** rejected as a product behavior. User selects a candidate channel and confirms a matching vault UUID; dialog/history API capability must be verified before implementation.
6. **Direct AES-GCM under VMK/FileVersion DEK:** rejected in proposed v2 because both roots span multiple operations and a rolled-back database cannot prove an uncommitted nonce was unused.
7. **Rotate VMK after every ambiguous wrap/rollback:** safer than repeating a possibly used VMK nonce if VMK itself were a GCM key, but causes broad wrapper/recovery/catalog migration and still needs durable handling of the replacement key. Proposed v2 instead keeps VMK out of GCM and derives one-use keys with fresh random salt and operation context. If VMK integrity or fresh entropy is uncertain, v2 still fails closed and requires reviewed root-key rotation/recovery.

## Open questions

- Independent expert approval of the one-use HKDF key derivations and their collision/entropy assumptions; complete v2 AAD registry/wire format; 96-bit IV and rollback lifecycle; aggregate GCM bounds; passphrase normalization; manifest-key Approach A; and key rotation/migration behavior.
- Final KDF profile after 8 GB M1 benchmarks and parser resource-budget review.
- Whether portable checkpoint export should be automatic after each commit, periodic, or user-managed; destination UX; and whether an unavailable export should block new backups. The current proposal updates Keychain per commit and exports after each commit when a destination is configured, warning if stale.
- Independent review of the exact checkpoint derivation/serialization and generation/verification of deterministic checkpoint vectors.
- Exact vault descriptor placement/versioning and whether remote storage of encrypted wrapper ciphertext is acceptable to the user.
- Exact channel dialog/history lookup methods and confirmation UX, checked against current official public docs before Phase 3.
- Keychain access controls and how new write epochs preserve decryptability of old epochs and recovery material.

## Independent review requirements

No independent cryptographic review or certification has occurred. Before implementation, obtain a reviewer qualified in applied cryptography to assess envelope bytes, AAD, nonce lifecycle/rollback, GCM bounds, KDF/passphrase handling, key wrapping, recovery-kit format, manifest rollback, and migration. Record reviewer scope, findings, remediation, and explicit human acceptance. A successful implementation test suite is not a substitute for this review.

## Security and migration implications

No cryptographic assurance is claimed. Once data exists, changes require explicit format migration and retained old-version decryptors; no in-place ciphertext rewrite. Any proposal change requires this ADR update and explicit approval before implementation. The new checkpoint binary format and single-binding logical schema supersede earlier vague checkpoint serialization and three-association-table descriptions in this planning package; no deployed bytes/schema exist, and no compatibility claim is made.

## Test impact

Design vectors for correct/incorrect passphrase and recovery, RFC 5869 primitive conformance plus PulakDrive recovery HKDF expected values (currently pending), Swift/Python normalization and Argon2 equivalence, every AAD field substitution, malformed field ordering/lengths, one-use key and nonce lifecycle at each crash boundary, DB/checkpoint rollback including unchanged-head ambiguous-wrapper case, modified/truncated/reordered chunks, unknown formats, malicious KDF values, manifest replay/fork/withholding, clean-Mac channel selection, and multi-epoch recovery. These are plans, not results.

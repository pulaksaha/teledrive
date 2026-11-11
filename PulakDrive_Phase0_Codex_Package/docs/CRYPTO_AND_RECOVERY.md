# Cryptographic Envelope and Recovery Kit — Proposed Phase 0 Contract

Status: Proposed design for independent cryptographic review, **not an implementation specification approved for coding yet**. No security claim is made. Do not implement until review closes the listed questions and the user approves the Phase 0 gate.

## Goals and threat boundaries

Protect content, names, and catalog structure from Telegram and remote observers; detect tampering, truncation, substitution, and chunk mix-ups; support recovery without the original Mac or Keychain. This does not protect plaintext from malware or another actor controlling the unlocked Mac account while files are open. SQLite metadata remains locally exposed according to host permissions unless separately reviewed DB encryption is approved.

## Proposed key hierarchy

- Vault Master Key (VMK): 32 random bytes from OS CSPRNG. It is HKDF input key material for one-use wrapping keys and is never used directly as an AES-GCM key. It does not encrypt manifests directly.
- Passphrase envelope: Argon2id derives a 32-byte wrapping key from user passphrase and random 16-byte salt; AES-256-GCM wraps VMK. Envelope records version, algorithm identifiers, parameters, salt, 12-byte nonce, ciphertext, and 16-byte tag.
- Recovery envelope: separate uniformly random 32-byte Recovery Secret (RS) from OS CSPRNG. HKDF-SHA-256 derives a one-use recovery wrapping key using the exact construction below, bound to vault UUID, recovery-kit UUID, crypto epoch UUID, and envelope UUID. AES-256-GCM wraps VMK once. The envelope ciphertext may be stored remotely for clean-Mac recovery; RS is never stored in Keychain, SQLite, or Telegram.
- Keychain stores a convenience-protected VMK copy or equivalent unlock material, supplementary to independent recovery. Exact Keychain item controls and access group require platform review.
- FileVersion DEK: fresh 32-byte random root key per immutable file version. It is never used directly as an AES-GCM key. For each chunk, derive a fresh one-use 32-byte chunk AEAD key using HKDF-SHA-256 with a fresh 32-byte CSPRNG salt and the exact chunk context below; encrypt exactly one chunk once with that derived key. The version DEK is wrapped using a separate one-use AEAD key derived from VMK.
- Manifest encryption recommendation: fresh random 32-byte manifest DEK per generation, used directly for exactly one manifest AES-GCM operation, then wrapped using a separate one-use AEAD key derived from VMK. This remains PROPOSED.

### Key use and one-use AEAD subkeys (proposed v2)

VMK and per-version DEKs are long-lived **HKDF input key material**, never direct AES-GCM keys. Every AES-GCM operation uses a separately derived or random one-use 32-byte AEAD key. Every encryption gets a fresh random 32-byte derivation salt where HKDF is used and a fresh CSPRNG-generated envelope UUID; crypto epochs and object IDs are also generated from OS CSPRNG UUIDv4 values, never rollback-prone counters. This addresses the case where an SQLite rollback erases evidence of a prior nonce reservation: the next operation uses fresh independent derivation inputs even when VMK or FileVersion DEK remains unchanged. Collision probability is negligible but nonzero; this is probabilistic, not a mathematical uniqueness guarantee, and requires independent review.

For VMK-derived key-wrap keys, including file-DEK and manifest-DEK wrappers:

1. Generate `salt` as exactly 32 bytes from the OS CSPRNG.
2. Set `IKM` to the 32 raw VMK bytes.
3. `PRK = HKDF-Extract-SHA256(salt, IKM)`.
4. Set `info` to the exact byte sequence `ASCII("PulakDrive/wrap-aead-key/v2") || 0x00 || vault_uuid[16] || crypto_epoch_uuid[16] || purpose:u16be || target_key_uuid[16] || envelope_uuid[16]`. The purpose value is exactly the authenticated tag-29 value: `3=file-DEK-wrap/v2` or `4=manifest-DEK-wrap/v2`.
5. `AEAD_KEY = HKDF-Expand-SHA256(PRK, info, 32)`. Because SHA-256 output length is 32 bytes, this is exactly `HMAC-SHA-256(key=PRK, data=info || 0x01)`; use the 32-byte output for exactly one AES-256-GCM encryption, then erase it best-effort.

For each chunk AEAD key, use the raw 32-byte FileVersion DEK as `IKM`, a fresh 32-byte CSPRNG `salt`, and:
`info = ASCII("PulakDrive/chunk-aead-key/v2") || 0x00 || vault_uuid[16] || crypto_epoch_uuid[16] || file_uuid[16] || file_version_uuid[16] || chunk_index:u64be || envelope_uuid[16]`.
Apply the same HKDF-Extract/Expand operations and 32-byte output. The derived key is used for exactly one chunk encryption. Chunk index is never sufficient by itself to derive the key; the fresh salt and envelope UUID are also mandatory.

For VMK passphrase wrapping, Argon2id output is a one-use AES-GCM key for exactly one VMK wrap. A new wrap attempt uses a fresh Argon2 salt and envelope UUID. For VMK recovery wrapping, the recovery HKDF output defined below is one-use for exactly one VMK wrap. A random manifest DEK is one-use for exactly one manifest encryption. No other AES-GCM operation may use VMK, FileVersion DEK, recovery secret, passphrase, or derived key directly. Checkpoint HMAC is not AES-GCM.

One-use means at most one encryption invocation under that AEAD key, not one upload attempt. Persist intent before encryption; after encryption, persist and verify the exact ciphertext. Upload retries reuse only those exact bytes. If ciphertext or metadata is lost or ambiguous, discard the salt/key/operation identifiers and derive new key material (or generate a new random manifest DEK); never repeat encryption with the previous derived key. A crypto epoch UUID is authenticated context, but does not by itself create a new key.

| Key material | Reuse and purpose | Freshness/nonce rule | Ambiguous outcome or rollback |
|---|---|---|---|
| VMK | Reused vault root; HKDF IKM only, never GCM key | Generate 32 random bytes once at vault creation; derived wrapper keys each use fresh 32-byte salt/context and one fresh reserved nonce | May remain HKDF IKM only if VMK integrity is trusted; never infer nonce safety from epoch/head. Rotate only through reviewed recovery if VMK integrity is uncertain. Old VMK remains needed for old wraps until migrated/verified. |
| Argon2id passphrase output | One GCM operation wrapping VMK | New 16-byte random Argon2 salt and envelope UUID per wrapper; reserve fresh nonce first | If uncertain, discard this derived key and use a fresh salt/envelope/nonce. Old passphrase envelope remains decryptable under its recorded parameters until replacement is verified. |
| Recovery HKDF output | One GCM operation wrapping VMK | Fresh 32-byte random HKDF salt and fresh envelope UUID; info binds vault, kit, crypto epoch, envelope | If uncertain, derive anew with fresh salt/UUID; preserve the user-held kit and old remote wrapper until the replacement wrapper is confirmed. |
| FileVersion DEK | Reused as HKDF IKM for chunks of exactly one immutable version; never a GCM key | Generate 32 random bytes per version; each chunk key gets fresh 32-byte salt/context and one reserved nonce | If source/version/root-DEK association is uncertain, abandon this DEK/version. Committed old versions remain decryptable through their retained wrappers. |
| Chunk AEAD key | One AES-GCM operation for one chunk | HKDF-SHA-256 from FileVersion DEK with fresh 32-byte salt, exact vault/epoch/file/version/index/envelope context; fresh reserved 12-byte nonce | If exact ciphertext is lost, never re-encrypt with this key or tuple; derive with fresh salt/envelope UUID/nonce. |
| Manifest DEK | One AES-GCM operation for one manifest generation | Generate 32 random bytes per generation; one fresh reserved 12-byte nonce | If ciphertext is ambiguous/lost, abandon this manifest key and generation attempt; retry with new manifest UUID, key and nonce. Historical manifest keys/wrappers remain available. |
| VMK-derived DEK-wrap key | One AES-GCM operation for one file or manifest DEK wrapper | HKDF-SHA-256 from VMK with fresh 32-byte salt, purpose, target key UUID, epoch and envelope UUID; one fresh reserved nonce | If wrapper output is ambiguous, do not repeat derivation tuple. Same VMK may derive a fresh one-use key only with new random salt and IDs; retain prior wrapper if recovered. |
| Checkpoint HMAC key | Reused only for HMAC checkpoint authentication, not AES-GCM | HKDF domain-separated from VMK; exact checkpoint format remains proposed | HMAC key reuse has no GCM nonce issue; rollback/freshness limitations remain. |

### Recovery HKDF-SHA-256 construction (proposed v2)

Decode the recovery-kit Base32 field to exactly 32 raw bytes; those bytes, without textual encoding, are `IKM`. `salt` is exactly 32 independently generated OS-CSPRNG bytes stored as raw bytes in the recovery envelope. Hash is SHA-256. Compute `PRK = HMAC-SHA-256(key=salt, data=IKM)` (HKDF-Extract). `info` is exactly `ASCII("PulakDrive/recovery-vmk-wrap/v2") || 0x00 || vault_uuid[16] || recovery_kit_uuid[16] || crypto_epoch_uuid[16] || envelope_uuid[16]`, UUIDs in canonical RFC 4122 network byte order. Since output length is 32 bytes, compute `OKM = HMAC-SHA-256(key=PRK, data=info || 0x01)` (the single HKDF-Expand block); all 32 output bytes form a one-use AES-256-GCM key for one VMK wrap. No implicit/default salt, text conversion, UUID formatting, label terminator, or output length is allowed. All context and salt fields are authenticated in envelope AAD. v2 fixes this construction; any change requires a new format version and migration. Separate recovery kits/epochs/envelopes derive separate keys through context and salt. Recovery document version 1 and crypto-envelope version 2 are independent version namespaces.

Deterministic vector specification (synthetic, not a credential): `IKM = 00 01 02 ... 1f`; the synthetic recovery-kit Base32 field is the unpadded uppercase RFC 4648 Base32 encoding of those 32 bytes; `salt = 20 21 22 ... 3f`; `vault_uuid = 00112233-4455-6677-8899-aabbccddeeff`; `recovery_kit_uuid = 10213243-5465-7687-98a9-bacbdcedfe0f`; `crypto_epoch_uuid = 20314253-6475-8697-a8b9-cadbecfd0e1f`; `envelope_uuid = 30415263-7485-96a7-b8c9-daebfc0d1e2f`. Construct `info` exactly as specified above. Expected `PRK` and 32-byte `OKM`: **PENDING vector generation and independent verification; do not invent outputs**. A separate HKDF primitive conformance case must match RFC 5869 Appendix A.1 (including PRK and OKM) before this PulakDrive vector is accepted. Swift/Python must match byte-for-byte for both vectors.

### Argon2id profile proposal

Propose RFC 9106 memory-constrained profile: Argon2id version 0x13, m=65,536 KiB, t=3, p=4, 16-byte random salt, 32-byte output. RFC 9106 identifies this as its second recommended option for memory-constrained environments. This is a proposal, not a claim of best product settings.

Passphrase input proposal: accept valid Unicode scalar values only; reject scalars unassigned in Unicode 15.1.0; normalize to NFC using **Unicode 15.1.0 normalization data**, then encode the normalized scalar sequence as shortest-form UTF-8 with no BOM. No platform-default normalization or replacement of invalid input is permitted. Reject unpaired surrogates/invalid scalar sequences, embedded U+0000, empty normalized input, and normalized UTF-8 longer than 1024 bytes. Preserve leading/trailing whitespace exactly; do not trim, case-fold, or map line endings. Swift and Python must use a pinned/bundled normalization implementation or data set that explicitly implements Unicode 15.1.0; relying on the OS/Python runtime's unspecified Unicode version is not conformant. Validate the implementation against Unicode 15.1.0 `NormalizationTest.txt` in addition to shared PulakDrive vectors. Profile ID `1=UTF8_NFC_UNICODE_15_1` is authenticated in AAD. Unsupported normalization profiles fail closed with an explicit unsupported-format error; never guess a profile. Changing Unicode data/profile requires a new profile ID and envelope migration. Add shared vectors for composed/decomposed accents, Hangul composition, supplementary scalars, leading/trailing spaces, unassigned scalars, invalid surrogates, NUL, empty input, and byte-length boundary; expected normalized bytes and Argon2id outputs must be independently generated and cross-checked between Swift/Python before implementation.

Generate a 16-byte salt from OS CSPRNG for each new passphrase envelope. For proposed format v2, accept only the exact registered profile: Argon2id version `0x13`, memory `65536 KiB`, iterations `3`, parallelism `4`, salt length `16`, output length `32`; each numeric field is encoded at its fixed width in the header registry. Before KDF execution validate the complete tuple against an explicit allowlist and safe hard bounds (memory 8,192–262,144 KiB, iterations 1–10, parallelism 1–8, salt exactly 16 bytes, output exactly 32 bytes); no unregistered tuple is accepted. These are denial-of-service bounds, not permission to accept arbitrary combinations. Unknown KDF/normalization/profile/version fails closed without fallback. Authenticate all KDF parameters, salt, profile ID, and encoding ID in canonical header AAD. Because AAD is checked only after derivation, strict pre-KDF allowlisting is mandatory. Profile parameters remain proposed pending independent review and 8 GB M1 benchmarking.

Benchmark methodology for minimum target (8 GB M1): record exact Mac model, macOS build, power mode, app/service build, and baseline memory pressure. After one warm-up, run 30 unlock derivations for the proposed profile; separately capture cold/warm median and p95 latency, peak process RSS/system pressure, CPU time, and failures. Repeat with service idle and representative transfer buffers active; allow one concurrent Argon2 invocation. Do not infer safety from one machine or tune down silently. Record commands/method/results; independent reviewer approves the latency/resource tradeoff.

KDF migration: after successful unlock with supported old profile, create a new passphrase envelope using reviewed profile, fresh salt, envelope UUID, and nonce; durably store and verify it, then retire old envelope only after recovery envelope is confirmed. Keep recovery envelope decryptable across passphrase changes. Envelope records profile/version for deterministic decoding. Unknown/unsupported profiles fail closed; migrations use an explicit old-profile decryptor and new-profile envelope.

## Canonical envelope serialization and AAD proposal

Proposed v2 envelopes use one canonical binary header and never rely on JSON canonicalization. Header bytes are the AAD supplied to AES-256-GCM byte-for-byte. The serialized form is:

```text
magic[8] = ASCII "PULAKDRV"
wire_version:u16be
envelope_type:u16be
header_length:u32be
field_count:u16be
fields[field_count]
```

Each field is `field_id:u16be || value_length:u32be || value[value_length]`. Fields appear exactly once in strictly increasing `field_id` order. Fixed-width integers are unsigned big-endian. UUID values are exactly 16 bytes in RFC 4122 network byte order; no textual UUIDs. Enumerations use fixed numeric registries. Byte strings are raw bytes. Text is forbidden in v2 cryptographic headers. The header ends after its last field; `header_length` must equal its exact byte length. Ciphertext and tag follow the header; ciphertext length is an authenticated field and must equal the number of ciphertext bytes before the final 16-byte tag.

Proposed v2 field tag registry (all integers are big-endian; `u8/u16/u32/u64` indicate exact field widths):

| Tag | Field | Encoding |
|---:|---|---|
| 1 | crypto-format version | `u16`; distinct namespace from the preamble `wire_version` |
| 2 | algorithm ID | `u16` enum |
| 3 | KDF ID | `u16` enum |
| 4 | KDF profile ID | `u16` enum |
| 5 | Argon2 version | `u8` |
| 6 | Argon2 memory KiB | `u32` |
| 7 | Argon2 iterations | `u32` |
| 8 | Argon2 parallelism | `u32` |
| 9 | passphrase encoding profile | `u16` enum |
| 10 | KDF/derivation salt | exact length by envelope type (32 bytes for HKDF; 16 for Argon2id) |
| 11 | derived/output key length | `u16` |
| 12 | vault UUID | 16 bytes |
| 13 | file UUID | 16 bytes |
| 14 | file-version UUID | 16 bytes |
| 15 | chunk index | `u64` |
| 16 | plaintext length | `u64` |
| 17 | ciphertext length | `u64` |
| 18 | nonce | 12 bytes |
| 19 | key UUID (VMK, DEK, or manifest DEK as specified by type) | 16 bytes |
| 20 | envelope UUID | 16 bytes |
| 21 | crypto epoch UUID | 16 bytes |
| 22 | manifest UUID | 16 bytes |
| 23 | manifest generation | `u64` |
| 24 | parent generation | `u64` |
| 25 | parent manifest UUID | 16 bytes |
| 26 | parent envelope SHA-256 | 32 bytes |
| 27 | recovery-kit UUID | 16 bytes |
| 28 | HKDF hash ID | `u16` enum |
| 29 | HKDF domain/purpose ID | `u16` enum |

Proposed v2 enum registry: `wire_version=2`; tag 1 `crypto_format_version=2`; the only currently registered supported pair is `(wire_version=2, crypto_format_version=2)` for every listed v2 envelope type. They are separate version namespaces even though both values are 2: `wire_version` selects the outer framing/parser grammar, while `crypto_format_version` selects cryptographic semantics, key schedule, and AAD rules. Envelope types `1=CHUNK`, `2=VMK_PASSPHRASE_WRAP`, `3=DEK_WRAP`, `4=MANIFEST`, `5=VMK_RECOVERY_WRAP`; algorithm `1=AES-256-GCM`; KDF `1=Argon2id`, `2=HKDF-SHA-256`; KDF profiles `1=Argon2id-v19-m65536KiB-t3-p4`, `2=HKDF-SHA256-one-use-v2`; passphrase profile `1=UTF8_NFC_UNICODE_15_1`; HKDF hash `1=SHA-256`; derivation domain/purpose IDs `1=recovery-vmk-wrap/v2`, `2=manifest-checkpoint/v1`, `3=file-DEK-wrap/v2`, `4=manifest-DEK-wrap/v2`, `5=chunk-aead-key/v2`. Exact binary labels and purpose values are defined in the derivation sections. Numeric IDs remain proposals, not implementation-approved registry entries.

Common preamble tags are not repeated as fields: `wire_version` is exactly 2, `envelope_type` is the registered enum, and both are authenticated as preamble bytes in AAD. Tag 1 `crypto_format_version` is required and authenticated as a TLV field. `magic`, `header_length`, and `field_count` are also included exactly as serialized in AAD. Only pair (2,2) is supported; reject any other pair before decryption, with no downgrade or fallback. A framing grammar change requires a new `wire_version`; a cryptographic semantic/key-schedule change requires a new tag-1 value; if both change, increment both. A new pair requires a reviewed migration and explicit approval. All v2 listed fields are required for their envelope type; no optional extensions. Header length is capped at 4096 bytes and field count at 32.

For each envelope type, field IDs and exact lengths are fixed by the v2 registry below. Unknown fields, duplicate/missing/reordered fields, unknown algorithm/type/version, nonzero reserved bits, integer overflow, inconsistent length, trailing bytes, or values outside explicit bounds are rejected before decryption. No permissive parsing or downgrade fallback. A future extensible format requires a new version and documented critical/noncritical field rules.

| Envelope type | Required authenticated fields (in field-ID registry order) |
|---|---|
| `CHUNK` | tag order: format version, AES-GCM ID, HKDF-SHA-256 KDF ID, HKDF profile ID (=2), 32-byte derivation salt, output key length `u16` (=32), vault UUID, file UUID, file-version UUID, chunk index `u64`, plaintext length `u64`, ciphertext length `u64`, fixed 12-byte nonce, FileVersion DEK UUID, envelope UUID, crypto epoch UUID, HKDF hash ID (=SHA-256), HKDF purpose ID (=5 chunk-aead-key/v2). Plaintext length must be 0–33,554,432 bytes. |
| `VMK_PASSPHRASE_WRAP` | tag order: envelope version, AES-GCM ID, KDF ID, KDF profile ID, Argon2 version, memory KiB, iterations, parallelism, passphrase encoding profile, 16-byte salt, output/key length (=32), vault UUID, ciphertext length (=32), fixed 12-byte nonce, VMK UUID, envelope UUID, crypto epoch UUID. |
| `DEK_WRAP` | tag order: envelope version, AES-GCM ID, HKDF-SHA-256 KDF ID, HKDF profile ID (=2), 32-byte derivation salt, output key length `u16` (=32), vault UUID, file UUID and file-version UUID (both all-zero only for manifest-DEK purpose), ciphertext length (=32), fixed 12-byte nonce, target DEK UUID, envelope UUID, crypto epoch UUID, manifest UUID (all-zero for file-DEK purpose), manifest generation (`0` for file-DEK purpose), HKDF hash ID (=SHA-256), HKDF purpose ID (=3 file-DEK-wrap/v2 or =4 manifest-DEK-wrap/v2). |
| `MANIFEST` | tag order: envelope version, AES-GCM ID, vault UUID, plaintext length, ciphertext length, nonce, manifest-DEK UUID, crypto epoch UUID, manifest UUID, generation `u64`, parent generation `u64` (zero only for genesis), parent manifest UUID (all-zero only for genesis), parent envelope SHA-256 (all-zero only for genesis). |
| `VMK_RECOVERY_WRAP` | tag order: envelope version, AES-GCM ID, HKDF-SHA-256 KDF ID, HKDF profile ID (=2), 32-byte salt, output key length `u16` (=32), vault UUID, ciphertext length (=32), fixed 12-byte nonce, VMK UUID, envelope UUID, crypto epoch UUID, recovery-kit UUID, HKDF hash ID (=SHA-256), recovery purpose ID (=1 recovery-vmk-wrap/v2). |

All listed header fields, including identifiers, lengths, algorithms, KDF parameters, salt, generation/parent link, and nonce, are authenticated because the complete canonical header is AAD. Ciphertext is authenticated/encrypted; the GCM tag authenticates the header and ciphertext. The nonce is also the GCM IV input; including it in AAD prevents envelope/header substitution. The `magic`, wire version, envelope type, and header length are authenticated as part of the header. Any duplicated context supplied by a caller or encrypted manifest must match the authenticated header exactly.

Pre-decryption parser caps proposed for v2: header <=4096 bytes and <=32 fields; chunk plaintext <=32 MiB; wrapped key plaintext exactly 32 bytes; descriptor envelope counts <=32 wrappers; manifest plaintext <=64 MiB pending catalog-scale review. Enforce total envelope size with checked arithmetic before allocation; stream ciphertext and reject lengths beyond cap. Total envelope bytes are exactly `header_length + ciphertext_length + 16-byte GCM tag`. A catalog exceeding the manifest cap needs a separately reviewed sharding/format ADR, not a silent cap increase.

Telegram channel title, message ID, caption, sender, timestamp, file reference, and server-reported size are transport/descriptive metadata, not cryptographic authority. They may be used for candidate lookup and diagnostics only after bounds checks. Do not make restore, version, or deletion decisions from these fields alone. Ciphertext digest is a transport check; GCM authentication is required.

## Chunk envelope proposal (proposed v2)

The canonical TLV header above is the only chunk wire format. There is no nonce-length field: nonce is always exactly 12 bytes in tag 18. The required CHUNK fields and order are exactly those in the registry table. With those fixed fields the header is exactly 304 bytes; total envelope length is exactly `304 + ciphertext_length + 16`, where GCM ciphertext length equals plaintext length and plaintext is at most 33,554,432 bytes. Maximum envelope size is 33,554,752 bytes. The final 16 bytes are the GCM tag and are not part of ciphertext or header AAD. `header_length` must equal 304 for CHUNK. Reject any length mismatch.

Use a 96-bit GCM nonce from OS CSPRNG, paired with a one-use derived chunk AEAD key (not the reusable FileVersion DEK). Persist salt, context, nonce, operation identity, and intent before encryption. An exact derived-key/context tuple may never be used for another encryption. Re-upload reuses exact ciphertext. If state is lost or ambiguous, use a new salt and envelope UUID to derive fresh key material; if source/version association is uncertain, abandon the FileVersion DEK and create a new immutable version. Each chunk has at most 32 MiB plaintext; envelope overhead must fit independently verified Telegram limits.

Every AES-GCM call uses a one-use key as specified above. Generate and durably reserve a fresh 96-bit nonce before encryption. Retries reuse exact ciphertext. If exact ciphertext is unavailable, create a new operation with fresh IDs/salt and therefore a fresh derived AEAD key; never repeat encryption under an existing key, even with different AAD or nonce. Nonce fields are serialized and included in vectors. Independent review must assess this construction and its GCM bounds.

For chunk envelopes, AAD is the entire canonical `CHUNK` header byte-for-byte; `envelope_type=CHUNK` and `wire_version=2` provide format/type separation. Proposed v1 used a contradictory chunk description and direct reuse of the FileVersion DEK; it is superseded before implementation because v2 derives one-use chunk keys and uses one fixed nonce encoding. If v1 data ever exists, migrate only through a separately approved decrypt-v1/re-encrypt-v2 process, verify the new objects, and retain old objects until verified. Never reinterpret v1 bytes as v2. Freeze registry IDs and vectors before coding.

## AES-GCM nonce lifecycle and rollback handling

- Generate every 96-bit nonce from the operating system CSPRNG. Never derive nonces from clocks, file offsets, counters that can roll back, or Telegram message IDs.
- Before an encryption call, commit a durable reservation record containing root-key UUID, crypto epoch, derivation salt, complete derivation context, envelope UUID, nonce, operation identity, and `reserved` state. The derived-key/nonce pair and the exact root/salt/context tuple must be unique in the active catalog. Then encrypt to an owner-only temporary ciphertext file, flush it, atomically promote it to durable staged ciphertext, and commit its digest plus `ciphertext_durable` state.
- Retry upload from the exact durable staged ciphertext. Do not call AES-GCM again. If exact ciphertext cannot be recovered, discard the one-use derived key and never reuse its salt/context/nonce tuple. Create a fresh salt, operation/envelope UUID and nonce, derive a fresh one-use key, then retry. Abandon the FileVersion DEK/version only if its integrity or source/version association is uncertain; an ambiguous wrapper does not itself require destroying a trusted VMK under the proposed derivation.
- Crash before reservation: no encryption is allowed to have begun; reserve a fresh nonce and proceed.
- Crash after reservation but before a verifiably durable ciphertext: outcome is ambiguous; mark the derived key and exact derivation tuple spent, never clear-and-reuse them. Create a new tuple/key for a new encryption operation; abandon the containing version only if its source/key association cannot be proven.
- Crash after staged ciphertext is durable: verify its length/digest against reservation, then resume upload using those exact bytes. If either record is missing/mismatched, quarantine and abandon that one-use AEAD key/operation; abandon the version only if its chunk plan or root DEK association is uncertain.
- Chunk DEKs belong to one immutable FileVersion only. On startup, any uncommitted version whose ciphertext/nonce state cannot be proven complete is abandoned; new upload gets a new FileVersion and fresh DEK. Never reuse a committed version's DEK for changed content.
- DEK-wrap keys are freshly derived one-use keys per wrapper; a manifest DEK is one-use for exactly one manifest encryption. On ambiguity, do not re-encrypt with the same derived key or manifest DEK. A trusted DEK/VMK root may remain in use only to derive fresh one-use keys with fresh salts and operation IDs under the proposed construction.

### Database rollback and snapshots

A nonce ledger stored only in SQLite cannot guarantee uniqueness if SQLite is restored to an earlier snapshot: the snapshot can erase evidence of reservations made later. Migration snapshots are not runtime rollback points. A DB restore enters crypto-recovery mode and pauses encryption. Compare DB crypto epoch/head with the independently stored Keychain checkpoint and reconcile the remote chain. If a trusted checkpoint establishes the head, preserve old keys and envelopes decrypt-only, abandon all possibly used uncommitted operation tuples, advance to a fresh crypto epoch UUID, and generate fresh salts and operation/envelope UUIDs for any new one-use derived AEAD keys. Continue only above the trusted generation with that head as parent. Existing verified recovery wrappers remain valid for the same VMK; if creating a replacement wrapper, verify its remote persistence before retiring any previous wrapper or kit.

**Explicit ambiguous-wrapper scenario:** Suppose a DEK wrapper was encrypted under a direct VMK AES-GCM key, its nonce reservation reached SQLite, then the DB is rolled back and neither the wrapper output nor reservation status can be proven, while the manifest head and Keychain checkpoint appear unchanged. Reusing that VMK directly for another AES-GCM wrap is **not safe**: the previous nonce may have been used, and the unchanged head/checkpoint says nothing about that local uncommitted encryption. The proposed v2 avoids this direct-use design: VMK is only HKDF IKM; each wrapper uses a fresh 32-byte salt and CSPRNG envelope UUID/context to derive a one-use AES-GCM key. After any detected or suspected rollback, pause and reconcile DB/remote/checkpoint state; never reconstitute or reuse an uncertain salt/context/key/nonce tuple. Obtain fresh OS-CSPRNG salt and IDs, derive a new wrapper key, reserve a fresh random nonce before encrypting, and persist exact ciphertext. If a silent snapshot rollback is not detectable because the visible manifest and checkpoint are unchanged, v2 still avoids reliance on DB counters for nonce safety because every subsequent operation independently creates fresh random derivation inputs; remote/local job reconciliation remains necessary, and rollback of all state sources cannot be detected. Under the proposed construction the same VMK may remain as HKDF IKM; a new VMK is not required solely because a wrapper operation is ambiguous, provided trusted VMK integrity and fresh CSPRNG operation inputs are established. A crypto epoch UUID alone is not sufficient. Independent review must validate this conclusion and the rollback procedure before implementation.

If freshness cannot be established (for example, both DB and checkpoint were rolled back or the checkpoint is missing), do not resume writes in the existing vault chain. Remain read/restore-only until the user explicitly chooses a reviewed recovery/new-vault branch procedure. Do not silently reset generation to zero, reuse an epoch/key, or claim that the old head is current.

This does not solve rollback of both SQLite and the external checkpoint, Keychain loss, or an attacker restoring every state source. In that case freshness cannot be proven. Safest behavior is read/restore-only until a new vault write epoch and recovery kit are explicitly established; never resume encryption using uncertain keys. This limitation and exact recovery ceremony require independent review. Database-backed tracking alone is insufficient.

### Proposed per-key limits

Proposed v2 limit: exactly one AES-GCM encryption invocation per derived/leaf AEAD key (chunk subkey, DEK-wrap key, manifest-wrap key, passphrase-wrap key, recovery-wrap key, or manifest DEK). A random nonce is still used and stored with the envelope. The 32 MiB chunk bound remains subject to applicable GCM per-invocation limits. The former `2^20 invocations per key` proposal applied to reused keys and is withdrawn for v2; independent review must calculate complete GCM bounds, including random-salt/key collisions and aggregate use under each root key.

Random 96-bit nonce collision risk is not mathematically zero. One-use keys and durable nonce/salt reservations limit consequences but do not substitute for cryptographic analysis of collision probabilities and GCM bounds.

SHA-256 ciphertext digest is for local transfer verification and local catalog. Whole-file plaintext SHA-256 may be stored locally for change detection/post-restore verification, but not sent remotely without equality-leakage review. AEAD tag validation is authoritative for chunk authenticity; hashes do not replace it.

## Manifest encryption, AAD, and rollback

Two approaches were compared:

| Approach | Advantages | Costs/risks |
|---|---|---|
| A. Random independent 32-byte manifest DEK per generation, wrapped using a VMK-derived one-use key | Strong generation/key isolation; fresh key makes nonce lifecycle simple; rotation can rewrap keys; orphan generation key can be abandoned after crash. | More random keys and wrap records; recovery/catalog must retain each manifest key; wrapper salt/context and staged-ciphertext lifecycle must be preserved. |
| B. Domain-separated manifest key derived from VMK | Fewer stored keys/wrap records; derivation is deterministic and operationally compact. | Generation/context encoding must never repeat; rollback can repeat derivation context; key rotation and generation fork behavior are more coupled; harder auditability. |

**Recommendation: A, PROPOSED only.** Create fresh random manifest DEK and manifest UUID for each generation; use it for exactly one manifest-encryption operation; wrap it using a fresh VMK-derived one-use key. Never reuse a key for a retry—retry exact durable ciphertext. Abandon manifest DEK/generation after ambiguous encryption outcome. A new generation after crash receives new manifest UUID and key even if the numeric generation would otherwise be reused. Independent review must evaluate key wrapping and full key hierarchy.

Manifest AAD is the full canonical `MANIFEST` header in the registry above, including vault ID, manifest ID, generation, parent generation/UUID/digest, key ID, lengths, algorithm/version, and nonce. The encrypted manifest body also carries the same linkage; reject mismatches.

Generation validation requires one genesis and each committed generation to reference the immediately preceding generation and its authenticated envelope digest. Duplicate generation with different manifest IDs is a fork: do not select a winner automatically; mark `needs_attention` and preserve both. A missing parent or nonmonotonic chain is invalid.

AEAD authenticates an individual manifest and its parent fields, but **does not prevent replay or rollback**. Keep a trusted-head checkpoint `(vault UUID, crypto epoch, generation, manifest UUID, envelope digest)` in Keychain after a remote commit is confirmed; reconcile crashes by comparing remote chain and local DB before advancing it. Keychain is a useful local rollback signal, not tamper-proof monotonic storage. For clean-Mac freshness, user may separately hold an HMAC-authenticated checkpoint as specified below. Without a trusted checkpoint, an attacker/service withholding newer Telegram messages can present an older valid chain without cryptographic proof that it is stale.

### Portable trusted-checkpoint serialization (proposed)

This is a separate fixed binary format, not an envelope and not JSON. The exact record is 188 bytes:

```text
magic[8] = ASCII "PULAKCHK"
checkpoint_wire_version:u16be = 1
record_length:u32be = 188
field_count:u16be = 8
fields in this exact order; each is field_id:u16be || value_length:u32be || value:
  1 vault_uuid[16]                 RFC 4122 network byte order
  2 crypto_epoch_uuid[16]          RFC 4122 network byte order
  3 manifest_generation[8]         unsigned u64 big-endian
  4 manifest_uuid[16]              RFC 4122 network byte order
  5 manifest_envelope_sha256[32]   raw digest bytes
  6 hmac_algorithm_id[2]           unsigned u16 big-endian; 1 = HMAC-SHA-256
  7 hmac_tag_length[2]              unsigned u16 big-endian; exactly 32
  8 hmac_tag[32]
```

Each field's length prefix is exactly six bytes. Record length is `16-byte preamble + 8 * 6-byte field prefixes + 124 value bytes = 188`. Fields 1–7 occupy bytes `[0,150)`; field 8 begins at byte offset 150. UUIDs must be nonzero RFC 4122 byte representations; generation is an unsigned 64-bit value, with zero reserved for the explicitly specified genesis checkpoint identity only. All byte order and lengths are fixed; no padding, optional fields, or extensions are accepted in version 1.

Derive the checkpoint HMAC key exactly as follows. `IKM` is the raw 32-byte VMK. `salt` is the raw 16-byte vault UUID in network byte order. HKDF hash is SHA-256; `PRK = HMAC-SHA-256(key=salt, data=IKM)`. Set `info = ASCII("PulakDrive/manifest-checkpoint-key/v1") || 0x00 || vault_uuid[16] || crypto_epoch_uuid[16]`. The one-block HKDF expand is `OKM = HMAC-SHA-256(key=PRK, data=info || 0x01)`, exactly 32 bytes. HMAC input is exactly `ASCII("PulakDrive/manifest-checkpoint-auth/v1") || 0x00 || record_bytes[0:150]`; tag is HMAC-SHA-256 with key `OKM`, exactly 32 bytes. Thus header, identities, digest, algorithm ID and tag length are covered; tag field ID/length are fixed by the strict parser and excluded from the MAC preimage. No implicit UUID text conversion, default salt, text terminator, or alternate encoding is allowed. This HKDF/HMAC key is never used for AES-GCM.

Reject any record not exactly 188 bytes; wrong magic/version/declared length/count; fields missing, duplicated, unknown, reordered, or wrong-width; unsupported algorithm/tag length; invalid/reserved UUID or generation combinations; truncated or trailing bytes; or HMAC mismatch. Verify HMAC in constant time. Unsupported versions fail closed. These rules and this format remain proposed pending review; deterministic test vectors are required before implementation and are not yet generated.

The record contains no secret key material and is not a substitute for the recovery kit. Freshness/export policy is also proposed: write the Keychain checkpoint after each confirmed manifest commit and, when the user has configured a destination, export/update the portable checkpoint after each commit. If portable export fails, report it as stale/pending and do not claim clean-Mac freshness; no checkpoint is silently uploaded to Telegram. Keychain-only provides no clean-Mac anchor; user export after every commit minimizes the portable rollback window but requires a reliable destination; periodic or manual export has a larger stale window. Selection of destination UX and whether export failure blocks new backups remain human decisions. HMAC authenticates a checkpoint, not its recency.

On a clean Mac, a checkpoint is a lower-bound/fork signal, not proof of the newest remote head. Accept a visible chain as a descendant only if it contains the exact checkpoint manifest UUID, generation, and envelope digest on a validated continuous ancestry. If the chain is behind, omits that checkpoint, or forks (including two identities/digests at one generation), stop writes and require explicit recovery. If Telegram withholds a newer manifest, even an exact checkpoint match cannot detect it; disclose that latestness is unknown and require user confirmation before treating the visible state as current or writing from it. If no checkpoint exists, freshness is unverifiable; remain read/restore-only by default until the user explicitly chooses a recovery branch. On loss of the original Mac, recover VMK from the mandatory kit and use any separately held checkpoint; the kit does not itself prove freshness. No cryptographic construction can detect an unseen head without an external trusted freshness anchor.

## Manifest commit

Manifest payload is canonical serialized data containing vault UUID, monotonically increasing generation, parent manifest digest/ID, entry/version state, chunk ordering/lengths, wrapped DEKs, encrypted paths, tombstones, and format identifiers. Encrypt/authenticate complete manifest before Telegram upload. Remote names/captions contain only opaque random IDs and minimal format markers; no plaintext paths, original names, hashes, or key material.

Upload encrypted chunks first. Persist each acknowledged opaque remote reference and verify identity/size. Publish manifest only after every referenced object is confirmed. Manifest publication is commit point. A crash before commit leaves unreferenced chunks; treat as orphans and do not automatically delete during MVP. Surface orphan accounting and retain until explicit purge policy. Invalid authentication, parent link, schema, bounds, or missing chunks makes manifest unusable for restore.

## Recovery kit proposal

The user-held recovery document contains the recovery secret and format metadata only. A separate **vault descriptor** remote object contains vault UUID, descriptor version, public KDF/profile identifiers, and encrypted passphrase/recovery VMK envelope ciphertexts. Publishing those ciphertext envelopes does not publish the recovery secret. The descriptor is readable only as ciphertext/opaque metadata until the user provides a passphrase or recovery secret.

Recovery document format v1 is ASCII, LF-delimited, exact ordered fields, no BOM, no unknown fields or whitespace folding:

```text
PULAKDRIVE-RECOVERY-V1
vault_id=<canonical lowercase UUID>
recovery_kit_id=<canonical lowercase UUID>
recovery_secret=<52 uppercase RFC 4648 Base32 characters, no padding>
checksum=<first 4 bytes of SHA-256("PulakDrive/recovery-kit/v1" || vault_uuid_bytes || kit_uuid_bytes || recovery_secret_bytes), lowercase hex>
```

Secret is 32 OS-CSPRNG bytes (256 bits). Decoder requires 52 Base32 characters and zero unused low padding bits in final symbol. Checksum detects transcription/corruption only; it is not authentication. Recovery-envelope AES-GCM authentication detects wrong/tampered secret. IDs are opaque identifiers, not credentials. Document contains no Telegram session, account token, filenames, channel invite link, plaintext VMK, encrypted wrapper, or other account credential. The recovery document/secret/checkpoint must not be uploaded to Telegram; only the separately encrypted vault descriptor/envelopes and encrypted manifests/chunks may be stored there.

Export ceremony: show secret once through native-controlled secure UI; allow explicit export to user-selected local/removable destination after warning about plaintext-secret handling. No cloud upload, clipboard auto-copy, analytics, or logs. Clear transient UI buffers best-effort; do not claim guaranteed zeroization in Swift/Python/runtime environments.

Verification challenge: require user to re-enter selected random character positions, then actually test-unlock a recovery envelope in memory and compare a VMK-derived verification value. Do not persist answer. Enable backup only after challenge and unwrap succeed. The checksum is only for error detection; successful AEAD unwrap is the cryptographic validation.

Clean-Mac recovery: install PulakDrive from trusted package; enter/import document through native secure UI; validate format/checksum and bounded parameters; separately authenticate Telegram through supported login flow; select and confirm vault channel as below; fetch the candidate vault descriptor; compare its vault UUID with the kit; derive recovery wrapping key; authenticate/decrypt remote VMK recovery envelope; then authenticate/decrypt manifest and restore through standard verify-to-temp/atomic-rename path. Compare any separately held trusted checkpoint. Kit alone cannot access Telegram. A missing/invalid descriptor is a recoverability failure, not permission to create a new vault.

### Channel discovery and confirmation

The recovery document intentionally contains no channel ID or invite link. After separate Telegram authentication, present a user-driven picker of private channels visible to that account (dialog-list API behavior must be verified against official Telegram/Telethon documentation before implementation). User selects a candidate; PulakDrive performs read-only candidate validation for its opaque vault UUID in a `vault descriptor` envelope/header, then authenticates the recovery wrapper using the supplied kit secret. Never select by title, latest message alone, or fuzzy matching. Display channel title and matching opaque vault UUID and require explicit user confirmation. If several candidates match, none match, history is unavailable, or API capability cannot be verified, stop and ask the user to select/confirm through Telegram's official client or provide a supported non-secret channel reference. Do not guess, create a channel, or send a probe message. Record exact read-only lookup methods in the Telegram adapter spec before Phase 3. Channel IDs/titles are locators, not cryptographic identity.

This is user-mediated selection, not automatic discovery. Listing dialogs and retrieving required history remain pre-implementation verification items.

Corrupt/unavailable kit: never claim recoverability. If Keychain still works, allow creating replacement secret/descriptor envelope, verify it, then retire old envelope only after explicit confirmation. If VMK is available nowhere, data is unrecoverable by design; do not create a new vault silently or overwrite old ciphertext. If checksum fails, do not attempt correction/guessing; allow retry from another user-held copy. If checksum passes but AEAD unwrap fails, report wrong kit, wrong channel/descriptor, or corruption without revealing which secret bytes were close.

## Key rotation and format migration

- Passphrase change: unlock VMK, create new salt/Argon envelope, verify, then retire old passphrase envelope. VMK/content unchanged.
- Recovery-secret rotation: create/export/verify replacement envelope/kit, then invalidate previous only after explicit confirmation.
- VMK rotation: keep the old VMK/recovery envelope available while unwrapping each old FileVersion DEK and manifest DEK, then write new wrappers derived from the new VMK and publish a new manifest generation. Existing chunk/manifest ciphertext may remain only if independent review approves; old manifests and wrappers remain necessary to decrypt prior generations until the new catalog and recovery path are verified by a clean restore. Retire old VMK/recovery material only after verification and explicit user confirmation. Requires migration plan and ADR before implementation.
- Format migration: authenticate/decrypt old format and write new immutable versions/manifest; never rewrite ciphertext in place. Retain old versions and recovery until new format verified.
- Unsupported future major format is rejected without destructive downgrade/fallback.

## Independent review questions

1. Is VMK/DEK/manifest key separation, including recommendation A, sound for this threat model?
2. Is canonical AAD field registry and binary encoding complete and unambiguous?
3. Are nonce reservation, crash/retry, DB rollback, key abandonment, and proposed per-key limits sufficient?
4. Are passphrase normalization and Argon2 profile/input bounds interoperable and safe?
5. Is recovery-kit checksum, entropy, export, and channel-confirmation ceremony adequate?
6. Is manifest checkpoint strategy adequate for rollback/fork detection and clean-Mac restore?
7. Are parser bounds safe against malicious remote data and KDF resource exhaustion?
8. Is SHA-256 placement appropriate without remote equality leakage?
9. Are key rotation and format migration complete and recoverable?

This is a review proposal only. AES-GCM/Argon2id use alone is not evidence of security.

# Decision Register

| ID | Decision | Status |
|---|---|---|
| D-01 | Native Swift macOS shell | Accepted |
| D-02 | React + TypeScript UI inside native shell | Accepted |
| D-03 | One Python core service process | Accepted |
| D-04 | Telethon is isolated adapter and sole MTProto owner | Accepted |
| D-05 | Dedicated private Telegram channel | Accepted |
| D-06 | 32 MiB initial application chunk target | Accepted as initial target; validate in Phase 0/3 |
| D-07 | AES-256-GCM + Argon2id algorithm families | Accepted baseline; exact envelope remains proposed in ADR-0007 and requires independent review |
| D-08 | Mandatory user-managed recovery kit; Keychain supplementary | Accepted; secret/document stays user-held; encrypted VMK wrapper ciphertext may be in remote vault descriptor |
| D-09 | Indefinite retention until manual deletion | Accepted |
| D-10 | One Mac writer per vault for MVP | Accepted |
| D-11 | Background service starts at user login | Accepted |
| D-12 | SQLite metadata/jobs; WAL and migrations | Accepted |
| D-13 | Watcher hints plus periodic full reconciliation | Accepted |
| D-14 | One upload and one download concurrently initially | Accepted as initial limit |
| D-15 | No automatic propagation of arbitrary Telegram-side deletion | Accepted |
| D-16 | No age-based garbage collection in MVP | Accepted |
| D-17 | Per-user LaunchAgent owns service startup/restart; Swift shell never launches a duplicate | Accepted direction; see ADR-0006 |
| D-18 | Authenticated loopback API with Keychain-protected per-install token; Swift owns API requests; React never receives token | Requirements accepted; bridge, native origin, token reload and WKWebView specifics need security review |
| D-19 | Proposed v2 canonical AAD, one-use HKDF-derived AEAD keys, recovery construction, manifest key Approach A, and RFC 9106 Argon2id profile | Proposed only; v1 proposal superseded before implementation; independent crypto review, vector generation/verification, and human approval required |
| D-20 | SQLite logical schema/state machines and safe migration/rebuild strategy | Documented logical contract; concrete SQL/migration implementation remains Phase 1 |
| D-21 | Telegram operations remain behind adapter; Phase 0 public docs only; live tests require separate explicit approval | Accepted |
| D-22 | Clean-Mac channel selection is user-mediated and confirms opaque vault UUID; no fuzzy/automatic channel choice | Proposed workflow; dialog/history API support must be verified before implementation |
| D-23 | AEAD does not prevent manifest replay/rollback; trusted head checkpoint is required for freshness claims | Accepted security limitation; exact 188-byte checkpoint serialization/HKDF/HMAC is proposed; export policy and vectors remain unresolved |
| D-24 | VMK and FileVersion DEK are never direct AES-GCM keys; each GCM operation uses one-use key material, so DB rollback cannot justify reusing a prior operation tuple | Proposed v2 crypto construction only; fresh HKDF salt/context/key derivation, rollback procedure, and root-key retention require independent review |
| D-25 | Proposed SQLite remote-object exclusivity uses one `remote_object_binding` entity keyed by `remote_object_id`, with a typed target identity and restrictive FKs | Proposed logical model supersedes three association tables; not an approved executable schema or migration; requires CHECK/trigger review and migration design |
| D-26 | Proposed envelope version namespaces distinguish framing `wire_version` from cryptographic `crypto_format_version` (tag 1); only (2,2) is registered | Proposed parser contract; no other pair accepted; requires vectors, review, and explicit approval |

Any change requires an ADR and user approval before implementation.

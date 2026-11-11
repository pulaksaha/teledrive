# Phase 0 Requirement Traceability and Closure

Date: 2026-11-12. Status is design/documentation evidence only; no implementation behavior is inferred.

| Requirement | Contract/document | Phase 0 criterion | Status after documentation pass |
|---|---|---|---|
| Product scope and exclusions | `PRODUCT_SPEC.md`, `ROADMAP.md`, root `GOALS.md` | P0-AC-01 | Documented; review for user acceptance remains. |
| Swift/React/Python boundaries | `ARCHITECTURE.md`, `RUNTIME_AND_LOCAL_API.md`, root `AGENTS.md` | P0-AC-02 | Documented; lifecycle/IPC implementation not tested. |
| One service/session owner; one vault writer | ADR-0004, `RUNTIME_AND_LOCAL_API.md` | P0-AC-03 | Documented; single-instance behavior unimplemented. |
| Local API auth/origin/CSRF and WKWebView bridge | `RUNTIME_AND_LOCAL_API.md`, `ARCHITECTURE.md` | P0-AC-04 | Native-owned token/bridge contract documented; custom-scheme origin and implementation review remain open. |
| Crypto envelope, hierarchy, nonce/AAD, versioning | `CRYPTO_AND_RECOVERY.md`, ADR-0007 | P0-AC-05 | Proposed v2 one-use AEAD hierarchy, derivation contexts, rollback response, and fixed chunk encoding documented; generated/verified vectors, independent review, and explicit approval remain outstanding. |
| Recovery independent of Keychain | ADR-0002, `CRYPTO_AND_RECOVERY.md` | P0-AC-06 | Kit/remote encrypted descriptor/channel confirmation design documented; clean-Mac recovery unimplemented/untested. |
| SQLite entities, states, migrations | `DATA_MODEL.md`, `SQLITE_SCHEMA_AND_STATES.md` | P0-AC-07 | Logical design documented; concrete schema and migration tests deferred. |
| Commit/restore/conflict/tombstone/purge | `SYNC_PROTOCOL.md`, `BACKUP_RESTORE_AND_FAILURES.md` | P0-AC-08 | Contract documented; behavior unimplemented. |
| Indefinite retention | ADR-0003, `PRODUCT_SPEC.md`, `BACKUP_RESTORE_AND_FAILURES.md` | P0-AC-09 | Accepted policy documented; no deletion implementation. |
| Telegram constraints from official docs, no connection | `TELEGRAM_ADAPTER_AND_RESEARCH.md` | P0-AC-10 | Public sources recorded with access date; limits remain dynamic; no account validation. |
| Crash/corruption/retry/restore/recovery test strategy | `PHASE_0_PLAN.md`, `BACKUP_RESTORE_AND_FAILURES.md`, `SQLITE_SCHEMA_AND_STATES.md` | P0-AC-11 | Planned; tests not run in planning phase. |
| Resource targets and measurement method | `ARCHITECTURE.md`, `BACKUP_RESTORE_AND_FAILURES.md` | P0-AC-12 | Targets/method documented; not measured. |
| Canonical AAD on all envelope types | `CRYPTO_AND_RECOVERY.md`, ADR-0007 | P0-AC-05 | Field registry and canonical TLV proposal documented; vectors/review outstanding. |
| Nonce lifecycle and DB snapshot rollback | `CRYPTO_AND_RECOVERY.md`, `BACKUP_RESTORE_AND_FAILURES.md`, `SECURITY_THREAT_MODEL.md` | P0-AC-05, 07, 11 | Direct VMK-as-GCM reuse after ambiguous rollback is explicitly unsafe. Proposed v2 keeps VMK as HKDF IKM and requires fresh one-use derivation tuples; independent review and fault-injection evidence remain outstanding. |
| Deterministic recovery HKDF | `CRYPTO_AND_RECOVERY.md`, ADR-0007 | P0-AC-05, 06 | Exact construction and synthetic input vector specified; expected PRK/OKM are pending generation and independent verification. RFC 5869 primitive conformance required. |
| Passphrase Unicode/Argon2 interoperability | `CRYPTO_AND_RECOVERY.md`, ADR-0007 | P0-AC-05, 12 | Unicode 15.1 NFC and UTF-8 rules pinned; platform implementation must bundle matching data; cross-language vectors and 8 GB M1 benchmark pending. Argon2 parameters remain proposed. |
| SQLite remote-reference exclusivity and descriptor mapping | `SQLITE_SCHEMA_AND_STATES.md`, `DATA_MODEL.md` | P0-AC-07, 08 | One proposed `remote_object_binding` entity, typed target, restrictive FKs, kind CHECK/trigger rules, and copy cardinalities are consistent; logical proposal only, no SQL/migration evidence or trigger tests. |
| Envelope framing and crypto version namespaces | `CRYPTO_AND_RECOVERY.md`, ADR-0007 | P0-AC-05 | `wire_version` and tag-1 `crypto_format_version` are distinct; only pair (2,2) supported; version compatibility tests/vectors and independent review remain outstanding. |
| Portable checkpoint serialization and freshness | `CRYPTO_AND_RECOVERY.md`, `BACKUP_RESTORE_AND_FAILURES.md`, `SECURITY_THREAT_MODEL.md` | P0-AC-05, 07, 11 | Exact proposed 188-byte format and HKDF/HMAC bytes are documented; generated/verified vectors and human export-policy decision remain outstanding; withheld-head freshness cannot be proven. |
| Manifest key strategy and replay/fork handling | `CRYPTO_AND_RECOVERY.md`, `BACKUP_RESTORE_AND_FAILURES.md` | P0-AC-05, 08 | Approach A recommended but proposed; checkpoint cannot detect withheld head absent trusted external anchor. |
| Recovery-kit format and channel confirmation | `CRYPTO_AND_RECOVERY.md`, `TELEGRAM_ADAPTER_AND_RESEARCH.md` | P0-AC-06, 10 | User-mediated selection proposed; dialog/history capability and clean-Mac drill remain unverified. |
| Argon2 passphrase normalization and M1 benchmark plan | `CRYPTO_AND_RECOVERY.md` | P0-AC-05, 12 | NFC/UTF-8 profile and test method documented; proposed parameters not benchmarked. |
| LaunchAgent exclusive ownership and no-spawn shell | `RUNTIME_AND_LOCAL_API.md`, `ARCHITECTURE.md`, ADR-0006 | P0-AC-02, 03 | Wording aligned; lifecycle tests not run. |
| No app code/Telegram operation in Phase 0 | root `AGENTS.md`, `PHASE_0_PLAN.md`, build log | P0-AC-13 | No such operation performed in this documentation task; code remains unimplemented. |
| No unresolved Critical/High risk | Review and ADRs | P0-AC-14 | NOT MET: independent crypto/recovery review and implementation decisions remain. |
| Explicit Phase 1 approval | root `AGENTS.md`, `PLANS.md`, `ROADMAP.md` | P0-AC-15 | NOT MET: no Phase 1 authorization in this task. |

## Closure checklist

- [x] Runtime and local API contract.
- [x] Proposed canonical AAD, one-use key/nonce/rollback, manifest, KDF, and recovery-kit contracts documented.
- [ ] Generate and independently verify deterministic recovery HKDF, passphrase normalization/Argon2, and envelope serialization vectors.
- [x] Logical SQLite schema, relationships, states, migration and rebuild strategy.
- [x] Transport-neutral Telegram contract, error mapping, dated official research.
- [x] Backup/restore, retention, failure, and resource contracts.
- [x] Requirement traceability matrix.
- [ ] Independent crypto design review and closure of findings.
- [ ] Human approval of proposed envelope details and remaining product choices.
- [ ] Final Phase 0 review finds no unresolved Critical/High risk.
- [ ] User accepts Phase 0 gate and separately authorizes Phase 1.

## Verdict

Phase 0 documentation is substantially specified but Phase 0 is **not complete**. Proposed v2 crypto parameters and recovery/checkpoint formats remain pending independent expert review; recovery and checkpoint expected vectors are not yet generated/verified; Argon2 M1 benchmarks and normalization vectors are pending; schema CHECK/trigger behavior has no implementation evidence; WKWebView custom-origin behavior, Keychain/service access, supported macOS minimum, channel dialog/history API behavior, and checkpoint export UX need review/decision. P0-AC-14 and P0-AC-15 are not met. No implementation, cryptographic certification, benchmark, or runtime test evidence is claimed.

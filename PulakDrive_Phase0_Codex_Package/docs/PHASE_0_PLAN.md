# Phase 0 Plan — Architecture Approval

## Objective

Turn the approved PulakDrive product direction into precise, reviewable engineering contracts. Phase 0 is documentation, analysis, and design validation only.

## Explicitly prohibited in Phase 0

- No application code or executable scaffolding.
- No dependency installation.
- No Telegram login, API calls, session creation, channel creation, channel inspection, messages, uploads, or downloads.
- No handling of real user files or secrets.
- No destructive filesystem or account operations.

## Work packages

### P0.1 — Requirements and scope
- Review `PRODUCT_SPEC.md`.
- Convert user outcomes into numbered functional and non-functional requirements.
- Identify ambiguous requirements and assumptions.
- Confirm MVP exclusions and indefinite retention behavior.

### P0.2 — Runtime and packaging design
- Specify Swift shell lifecycle and embedded React presentation.
- Specify Python helper launch, supervision, shutdown, and version compatibility.
- Follow the approved decision: the per-user LaunchAgent exclusively owns service startup/restart; Swift shell uses supported Service Management controls and never spawns Python. Specify and verify single-instance locking/supervision.
- Define local API/IPC, authentication, port discovery, origin validation, and CSRF defenses.
- Define app/service update compatibility and migration sequencing.

### P0.3 — Cryptography and recovery design
- Specify key hierarchy, envelope formats, serialization, versioning, nonce generation, AAD, and key rotation.
- Select and justify Argon2id parameters; benchmark plan must be defined, not executed against real secrets.
- Define recovery-kit entropy, representation, export, user ceremony, verification, and failure UX.
- Specify zeroization limits and secret lifetime where practical.
- Produce test vectors and adversarial test cases, including the distinct `wire_version` / tag-1 `crypto_format_version` pair and portable checkpoint binary serialization/HKDF/HMAC vectors. Expected cryptographic outputs must be generated and independently checked; documentation examples are not evidence.
- Obtain an independent crypto design review before Phase 1.

### P0.4 — Persistence and state machines
- Produce ER diagram and schema draft.
- Define Job, FileVersion, Conflict, Tombstone, and purge state machines.
- Define transaction boundaries, idempotency keys, migration policy, crash recovery, and DB backup/rebuild strategy.
- Define indefinite retention and graph-based purge scope.

### P0.5 — Sync and Telegram adapter contract
- Define transport-neutral object interface.
- Define adapter methods, error taxonomy, retry policy, ambiguous-send reconciliation, and remote object identity.
- Research current official Telegram API/Telethon documentation for terms, file-size limits, upload part constraints, rate-limit behavior, and account restrictions.
- Record source URLs and access date in an ADR/research note.
- **Documentation research only; do not connect to Telegram or test an account.**
- Confirm that app-level 32 MiB chunking is independent of MTProto protocol part size.

### P0.6 — Threat model and privacy
- Review `SECURITY_THREAT_MODEL.md`.
- Classify every data field and identify what is visible to Telegram.
- Analyze malicious local web origin, same-user malware, account/session compromise, remote tampering, metadata leakage, and loss of recovery material.
- Define security logging and diagnostics redaction.

### P0.7 — Test and resource strategy
- Define unit, integration, contract, fault-injection, security, recovery, and end-to-end test layers.
- Define synthetic test data only.
- Define target hardware and repeatable memory/CPU/disk measurement procedure.
- Validate the proposed <150 MB idle and <400 MB active targets as targets to test, not guarantees.
- Define staging-space backpressure and disk-full behavior.

### P0.8 — Review and gate
- Conduct architecture review.
- Resolve critical/high findings.
- Update ADRs and roadmap.
- Produce a Phase 0 verification report.
- Ask the user for explicit Phase 1 authorization.

## Required Phase 0 artifacts

1. Numbered requirements traceability matrix.
2. Component and deployment diagrams.
3. Local API/IPC contract, including auth and origin rules.
4. Crypto envelope proposal with distinct framing/crypto version namespaces, deterministic recovery and trusted-checkpoint vector specifications; expected values must be generated, independently verified, and reviewed before implementation.
5. Recovery-kit format and verification ceremony.
6. Data classification and privacy table.
7. ER diagram and state machines.
8. Telegram adapter contract and documentation-only feasibility research.
9. Failure-mode/retry matrix.
10. Test strategy and resource measurement plan.
11. Updated ADRs and risk register.
12. Phase 0 verification report.
13. `RUNTIME_AND_LOCAL_API.md` lifecycle, token, loopback, origin, CSRF, port discovery, and compatibility contract.
14. `CRYPTO_AND_RECOVERY.md` proposal and independent review record; no implementation approval until review closes.
15. `SQLITE_SCHEMA_AND_STATES.md` relationship map (including exclusive remote-object binding), state machines, migration and rebuild strategy.
16. `TELEGRAM_ADAPTER_AND_RESEARCH.md` neutral adapter contract, error mapping, and dated official documentation sources.
17. `BACKUP_RESTORE_AND_FAILURES.md` bounded transfer, staging, commit, restore, retention, and failure protocol.
18. `PHASE_0_TRACEABILITY.md` requirement-to-document-to-acceptance-criterion status matrix.

## Acceptance criteria

| ID | Mandatory criterion |
|---|---|
| P0-AC-01 | Product scope, MVP outcomes, and non-goals are unambiguous. |
| P0-AC-02 | Swift shell, React UI, Python service, and Telegram adapter boundaries are documented. |
| P0-AC-03 | Single-process/session ownership and single-writer vault constraints are explicit. |
| P0-AC-04 | Local API/IPC authentication and cross-site protections are specified. |
| P0-AC-05 | Crypto envelope, key hierarchy, nonce/AAD rules, and versioning are specified. |
| P0-AC-06 | Recovery kit can be independently reviewed and does not depend on original Keychain. |
| P0-AC-07 | SQLite entities, relationships, state machines, and migration strategy are documented. |
| P0-AC-08 | Backup commit, restore, conflict, tombstone, and purge semantics are precise. |
| P0-AC-09 | Indefinite retention is the default; no age-based deletion is designed into MVP. |
| P0-AC-10 | Telegram limitations and risks are researched from current official documentation without connecting. |
| P0-AC-11 | Test strategy includes crash, corruption, retry, restore, and recovery scenarios. |
| P0-AC-12 | Resource targets and measurement method are documented. |
| P0-AC-13 | No application code or Telegram operation was performed during Phase 0. |
| P0-AC-14 | No unresolved critical/high architecture, security, or data-loss issue remains. |
| P0-AC-15 | User explicitly approves Phase 1 before implementation begins. |

## Phase 0 gate decision

- **PASS:** All mandatory criteria met; user may authorize Phase 1.
- **PASS WITH EXCEPTIONS:** Only non-critical exceptions remain and the user explicitly accepts each.
- **FAIL:** Any mandatory criterion fails, or a critical/high risk remains unresolved.

Codex must not mark the phase complete or start Phase 1 without reporting the evidence for each criterion.

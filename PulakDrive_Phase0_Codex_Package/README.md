# PulakDrive — Phase 0 Planning Package

This repository package defines the product, architecture, security constraints, seven-phase roadmap, and Codex workflow for PulakDrive.

**This package is planning-only.** It does not contain application implementation code and does not authorize Telegram access, login, channel creation, message uploads, or downloads.

## Product in one sentence

PulakDrive is a Mac-first personal backup and synchronization application that encrypts user files locally, stores encrypted chunks and committed manifests in a dedicated private Telegram channel through the user's own Telegram account, and supports reliable restore and version recovery.

## Approved baseline decisions

| Area | Decision |
|---|---|
| macOS application shell | Native Swift shell |
| User interface | React + TypeScript, presented inside the native shell |
| Core service | One Python service process |
| Telegram integration | Telethon behind one isolated adapter |
| Remote storage | Dedicated private Telegram channel |
| Large files | Application-level chunking; initial target 32 MiB per encrypted chunk |
| Local metadata | SQLite, migrations, WAL, foreign keys |
| Encryption | AES-256-GCM; Argon2id-based key derivation/wrapping |
| Recovery | Mandatory user-managed recovery kit; Keychain is supplementary |
| Deleted-file retention | Indefinite, until manually deleted |
| Vault topology | One Mac per vault for MVP |
| Startup | Background service starts at user login |
| MVP concurrency | Initially one upload and one download at a time |
| Filesystem monitoring | FSEvents/Watchdog hints plus periodic full reconciliation |
| Sync semantics | Immutable versions, explicit tombstones, conflict preservation; no timestamp-based last-write-wins |

## Read this first

1. `AGENTS.md` — mandatory instructions for Codex and contributors.
2. `docs/PRODUCT_SPEC.md` — scope, user stories, and non-goals.
3. `docs/ARCHITECTURE.md` — component boundaries and runtime design.
4. `docs/SECURITY_THREAT_MODEL.md` — security objectives, threats, and controls.
5. `docs/SYNC_PROTOCOL.md` — backup, commit, restore, deletion, and conflict semantics.
6. `docs/RUNTIME_AND_LOCAL_API.md` — LaunchAgent ownership, lifecycle, and authenticated loopback contract.
7. `docs/CRYPTO_AND_RECOVERY.md` — proposed envelope and recovery kit; pending independent cryptographic review.
8. `docs/DATA_MODEL.md` and `docs/SQLITE_SCHEMA_AND_STATES.md` — logical entities, relationships, state machines, migration/recovery rules.
9. `docs/TELEGRAM_ADAPTER_AND_RESEARCH.md` — transport boundary and dated official-doc research.
10. `docs/BACKUP_RESTORE_AND_FAILURES.md` — bounded backup/restore, retention, and failure behavior.
11. `docs/PHASE_0_TRACEABILITY.md` — requirement-to-document-to-acceptance status and Phase 0 closure checklist.
12. `docs/ROADMAP.md` and `docs/PHASE_0_PLAN.md` — phase roadmap and Phase 0 exit criteria.
13. `docs/adr/` — architecture decisions, including proposed crypto ADR-0007.
14. `prompts/` — Codex prompts for planning, implementation, verification, and closure.

## Repository status

The repository starts in **Phase 0: Architecture approval**. Codex must not implement application code until Phase 0 is accepted and the user explicitly authorizes Phase 1.

## Proposed repository layout

```text
pulakdrive/
├── AGENTS.md
├── README.md
├── docs/
│   ├── PRODUCT_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── SECURITY_THREAT_MODEL.md
│   ├── DATA_MODEL.md
│   ├── SYNC_PROTOCOL.md
│   ├── ROADMAP.md
│   ├── PHASE_0_PLAN.md
│   ├── CODEX_WORKFLOW.md
│   └── adr/
│       ├── ADR-0001-native-swift-shell.md
│       ├── ADR-0002-cryptographic-recovery.md
│       ├── ADR-0003-retention-and-deletion.md
│       ├── ADR-0004-single-process-and-vault-topology.md
│       └── ADR-0005-telegram-as-remote-replica.md
└── prompts/
    ├── 00-phase0-review.md
    ├── 01-phase0-plan.md
    ├── 02-phase-implementation-template.md
    ├── 03-independent-verification-template.md
    ├── 04-remediation-template.md
    └── 05-phase-closeout-template.md
```

## Important product warning

Telegram is a transport and remote-replica location, not a guaranteed archival-storage service or a substitute for an independent backup. PulakDrive must clearly surface remote degradation, rate limits, account/session problems, missing objects, and recovery limitations. Do not claim that a successful upload alone proves long-term recoverability.

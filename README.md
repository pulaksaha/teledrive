# PulakDrive

PulakDrive is a macOS personal-backup project designed to encrypt data locally and use a dedicated private Telegram channel as a best-effort remote replica.

The current repository contains only the **Phase 1, Milestone 1 development foundation**. It does not perform real backups, encryption, filesystem scanning, restore, synchronization, or Telegram operations.

## Approved target architecture

The approved design separates responsibilities across three components:

```text
Native macOS shell (Swift)
  - Owns the future application lifecycle and native UI integration
  - Will discover and communicate with one Python service instance
  - Must not independently create duplicate service instances

React + TypeScript UI
  - Will be embedded by the native shell through WKWebView
  - Must not directly access secrets, the filesystem, or Telegram

Python core service
  - Will own SQLite, backup orchestration, and the isolated Telegram adapter
  - Will expose a future authenticated loopback API to the native shell

Private Telegram channel
  - Planned as a best-effort remote replica, not guaranteed archival storage
```

The design calls for AES-256-GCM, Argon2id, a VMK/DEK hierarchy, and initially 32 MiB plaintext chunks. Those are architecture decisions only; none of that production functionality is implemented in this milestone.

## Repository layout

```text
telegramdrive/
├── apps/
│   ├── macos/                         # Swift package, mock executable, and tests
│   └── web/                           # React, TypeScript, Vite, and Vitest foundation
├── services/
│   └── core/                          # Python models, configuration, mocks, and tests
├── packages/
│   └── contracts/                     # Hand-maintained TypeScript domain contracts
├── scripts/                           # Repository build, test, and lint entry points
├── PulakDrive_Phase0_Codex_Package/   # Architecture and security design records
├── harness/                           # Earlier Phase 0 verification records
├── AGENTS.md                          # Repository governance
├── BUILD_LOG.md                       # Observed Milestone 1 verification results
└── README.md
```

## Development prerequisites

The latest verified toolchain is:

- macOS
- Swift 6.1.2
- Python 3.12.14
- Node.js 26.5.0
- npm 11.17.0

Swift 6+, Python 3.12+, and a Node.js/npm version compatible with the pinned frontend dependencies are required.

## Installation

### Python

Create the project virtual environment and install the exact direct dependency pins:

```bash
cd services/core
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
```

### Frontend

Install from the committed npm lockfile:

```bash
cd apps/web
npm ci
```

Swift dependencies are resolved by Swift Package Manager when a Swift build or test is run.

## Build, test, and lint

From the repository root:

```bash
./scripts/build.sh
./scripts/test.sh
./scripts/lint.sh
```

Each script resolves the repository root relative to its own location, fails on the first unsuccessful command, and can therefore be invoked by path from a different current directory. The scripts do not reset Git or delete user data.

Run component checks directly when needed:

```bash
# Swift
cd apps/macos
swift test

# Python
cd services/core
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .

# Frontend
cd apps/web
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

The root build currently runs `swift build`, Python source compilation with `compileall`, and the Vite production build. It does not produce a Python wheel or application installer.

## Current implementation

### Swift

- Swift Package Manager package and safe command-line entry point.
- Domain status enums and an application-status value type.
- Six unit tests.
- No macOS application lifecycle, WKWebView bridge, LaunchAgent integration, Keychain access, or service process management.

### Python

- Pydantic configuration and domain models.
- Domain error hierarchy.
- Structured logging and foundational exact-name redaction.
- In-memory status and vault repositories.
- Mock application service coordinator.
- Fifty-two tests and a clean Ruff check.
- Placeholder API, database, and jobs packages only; there is no running FastAPI application or SQLite implementation.

### Shared contracts

- Hand-maintained TypeScript enums and interfaces mirroring the current serialized Python domain models.
- Snake-case serialized field names, explicit required fields, and explicit nullable backup timestamp.
- Protocol major/minor fields document the compatibility boundary.
- No generated client or production API schema.

### Frontend

- React 18, TypeScript, and Vite foundation.
- Static dashboard backed only by deterministic mock data.
- Explicit unconfigured-vault and no-backup states.
- Vitest and Testing Library coverage that prevents a false successful-backup report.
- No Python API connection, native bridge, credentials, or backup controls.

## Deferred and blocked functionality

The following functionality is not implemented and remains outside Milestone 1:

- Production AES-GCM encryption or decryption.
- Argon2id password derivation and the production VMK/DEK hierarchy.
- Recovery-kit generation or verification.
- Keychain storage of real secrets.
- Real bearer-token authentication or a production network API.
- Production WKWebView bridge.
- LaunchAgent registration or background startup.
- Telegram, Telethon, or channel operations.
- Real filesystem scanning, FSEvents, or Watchdog.
- SQLite domain schema or migrations.
- Real backup, synchronization, restore, retention, or purge operations.

The Phase 0 design package still contains unresolved review and approval gates. Milestone 1 does not resolve or bypass them.

## Known limitations

- Telegram is designed as a best-effort replica and cannot be treated as guaranteed archival storage.
- The MVP design permits one Mac writer per vault; this behavior is not implemented yet.
- Deleted-file retention is designed to be indefinite until manual deletion; no retention engine exists yet.
- Python direct dependencies are exactly pinned, but a hash-locked transitive dependency file was not generated because package-index resolution was unavailable in the execution environment.
- The Python root build validates source compilation rather than building a wheel or source distribution.
- Frontend installation currently emits upstream deprecation/support notices for some pinned development dependencies; installation, checks, tests, and build still succeed.
- The verified `npm ci` run reported 19 dependency audit findings (7 low, 9 moderate, 1 high, and 2 critical). No unreviewed automatic or forced dependency upgrade was applied.
- Logging redaction is a foundation, not a comprehensive secret-scrubbing guarantee.

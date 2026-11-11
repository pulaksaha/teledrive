# Architecture

## 1. Architectural shape

PulakDrive uses three logical layers and one runtime service process.

```text
┌──────────────────────────────────────────────┐
│ Native macOS application shell (Swift)       │
│ - lifecycle, permissions, menu/status        │
│ - secure setup and recovery UX                │
│ - embedded React UI (WKWebView)               │
│ - Keychain bridge / native capabilities       │
└──────────────────────┬───────────────────────┘
                       │ authenticated local IPC/API
┌──────────────────────▼───────────────────────┐
│ One Python service process                   │
│ FastAPI local API                             │
│ Vault / Crypto / Manifest / Sync coordinator  │
│ Filesystem scan + watcher + reconciliation   │
│ Durable job queue + SQLite repositories      │
│ Telegram repository adapter                  │
└──────────────────────┬───────────────────────┘
                       │ MTProto through Telethon only
┌──────────────────────▼───────────────────────┐
│ User's Telegram account                      │
│ Dedicated private channel                   │
│ Encrypted chunks + encrypted manifests       │
└──────────────────────────────────────────────┘
```

The React UI is a presentation layer. It must not access SQLite, cryptographic keys, the filesystem backup engine, or Telethon directly.

The per-user LaunchAgent is the only component that executes/restarts the Python service. Swift may register, unregister, or request restart through supported Service Management controls, and it may discover/communicate with the existing process; it must never spawn a second service or signal an arbitrary PID.

## 2. Native shell

Swift is the approved application shell.

Responsibilities:
- Own macOS app lifecycle, menu-bar/status integration, notifications, permission prompts, and LaunchAgent registration controls.
- Host the React interface in a controlled WKWebView or another explicitly approved native-web presentation.
- Provide a narrow, documented allowlist bridge for typed UI commands; never expose the bearer token or generic API proxy to JavaScript.
- Own authenticated UI-to-service API requests and Keychain access for the per-install token; the service reads the scoped Keychain item to validate requests.
- Discover and monitor the existing LaunchAgent-owned Python service. The Swift shell must never spawn or independently start a Python process. User stop/restart/enable/disable goes through supported Service Management/LaunchAgent controls, never raw PID signals or shell commands.
- Avoid exposing arbitrary native methods to web content.

The baseline is a signed native shell and bundled Python service running in the logged-in user's context. A per-user LaunchAgent exclusively owns service startup and crash restart; UI presentation may start only when the user opens the app. Detailed lifecycle and API contract is in `RUNTIME_AND_LOCAL_API.md`.

## 3. Python service

One service process owns:
- FastAPI local control API;
- SQLite connection lifecycle and migrations;
- durable job queue;
- filesystem scan and watcher coordination;
- cryptographic operations;
- manifest construction and validation;
- sync state machine;
- the single Telethon client/session owner.

Do not split Telethon into a second service for MVP. A single process reduces session contention and simplifies SQLite write ownership.

Long-running transfers are durable jobs. HTTP requests create, inspect, pause, or cancel jobs; they do not remain open for the duration of a file transfer.

## 4. Local API security

- Bind only to loopback.
- Reject requests unless Host is the exact numeric loopback address and Origin is the exact trusted native UI origin set by Swift. Reject untrusted/null browser origins; no wildcard CORS.
- Require per-install Keychain token in Authorization header and a per-native-session anti-CSRF nonce. Swift makes API requests; React receives only typed responses through an allowlisted bridge and never sees long-lived auth material.
- Restrict WKWebView navigation to signed bundled UI, apply restrictive CSP, block remote subresources/popups/frames, and reject arbitrary bridge commands.
- Use strict request schemas and size limits.
- Do not expose arbitrary filesystem paths or shell execution endpoints.
- Avoid wildcard CORS.
- Do not assume loopback alone is an authentication boundary.
- Keep the API unavailable to remote network interfaces.
- Document port selection, process discovery, and stale-process handling in Phase 0.

## 5. Persistence

SQLite stores metadata and job state, not file content.

- Store in the user's Application Support directory.
- Enable foreign keys and WAL; use migrations.
- Keep transactions short.
- Use a single logical writer.
- Persist job intent before network side effects.
- Use stable IDs and idempotency markers.
- Avoid logging plaintext paths unless necessary; consider encrypted path/catalog fields.
- SQLite metadata is not automatically protected by file-content encryption. MVP baseline: macOS account permissions and FileVault, minimize stored metadata, and document residual exposure. Decide whether database-level encryption is needed before release.

## 6. Filesystem monitoring

Watcher events are hints only. Use FSEvents/Watchdog to reduce latency, then reconcile against periodic full scans.

- Debounce noisy events.
- Wait for files to become stable before reading.
- Detect changes during hashing or streaming.
- Reconcile after watcher overflow, service restart, sleep/wake, and permission changes.
- Avoid treating app-originated restore writes as new user edits; use a controlled write marker or equivalent suppression mechanism.

## 7. Telegram adapter

Telethon is isolated behind a repository/transport interface.

Only this adapter may:
- create/use the MTProto client;
- read/write the Telegram session;
- resolve the configured private channel;
- send and retrieve encrypted objects.

No UI, API handler, or sync business service may import Telethon directly.

The adapter must support retryable rate limits, flood waits, expired file references, ambiguous send outcomes, and missing objects. Treat Telegram responses as untrusted transport data and validate all retrieved object metadata before use.

Phase 0 may document the adapter contract and research limits, but must not connect to Telegram.

## 8. Memory and transfer limits

Initial engineering targets for an 8 GB Apple Silicon Mac:
- idle service memory target: below 150 MB;
- active transfer target: below 400 MB;
- one upload and one download concurrently;
- 32 MiB application-level encrypted chunks;
- bounded streaming buffers and bounded staging space.

These are targets to measure, not guarantees. Record methodology and observed results. Avoid holding entire files, full ciphertext, or all chunks in memory.

## 9. Packaging and startup

- Native Swift shell packaged as a macOS application.
- Python service/helper bundled and signed as part of the distribution.
- Per-user LaunchAgent starts the service at login.
- Service runs in the logged-in user's context so Keychain access and file permissions behave predictably.
- UI shell and service communicate through authenticated loopback API or a narrowly scoped local IPC mechanism.
- Graceful shutdown persists job state and releases the Telegram session.
- Startup must detect incompatible versions, stale processes, locked Keychain, and incomplete migrations safely.

Exact signing, notarization, helper packaging, and update strategy are Phase 5/6 design and verification work.

The authoritative lifecycle, LaunchAgent ownership, authenticated loopback API, native-owned token, WKWebView bridge/origin, token rotation, port discovery, and compatibility contract is `RUNTIME_AND_LOCAL_API.md`. Token bootstrap and embedded-web origin behavior remain subject to implementation security review.

## 10. Proposed source layout after implementation authorization

```text
apps/
  macos/                 # Swift native shell
  web/                   # React + TypeScript UI
services/
  core/                  # Python service
    api/
    application/
    domain/
    repositories/
    crypto/
    filesystem/
    sync/
    telegram_adapter/
    migrations/
packages/
  contracts/             # versioned API/schema contracts
tests/
  unit/
  integration/
  security/
  recovery/
  fixtures/
docs/
```

This is a logical layout, not a mandate to create it during Phase 0.

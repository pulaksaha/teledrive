# PulakDrive Goals

## Product goal

Deliver a local-first, recoverable personal backup and two-way synchronization application for macOS on Apple Silicon. Encrypt content, paths, and manifests before remote transfer; local SQLite metadata is not automatically encrypted and its at-rest protection remains an explicit design decision. Use a dedicated private Telegram channel through the user's account as a best-effort remote replica, and make failures and recovery state visible. Telegram is not an unrestricted second editing location.

## MVP goals

- Establish a local vault with a tested, user-managed recovery path independent of the original Mac's Keychain.
- Reliably scan selected folders, detect changes, and resume durable jobs after restart.
- Back up encrypted, chunked immutable versions through the isolated Telegram adapter.
- Restore files only after authentication and integrity checks, without damaging an existing destination on failure.
- Preserve deleted files, historical versions, and both sides of conflicts until explicit manual purge.
- Operate as a native macOS product with a React UI and one Python service process.
- Maintain bounded memory and staging use on an 8 GB Apple Silicon Mac.

## Engineering goals

- Protect confidentiality, integrity, and recoverability; avoid unsupported security claims.
- Keep one process and one logical SQLite writer for the MVP.
- Keep Telegram and OS capabilities behind narrow adapters.
- Make state transitions, retries, and uncertain remote outcomes durable and observable.
- Verify every phase independently against its acceptance criteria.

## Non-goals for MVP

Multi-device concurrent writers, public sharing, mobile clients, other cloud providers, public internet access, teams, content search, equality-leaking deduplication, age-based garbage collection, or treating Telegram as immutable/SLA-backed storage.

## Current goal

Complete Phase 0 architecture approval: resolve contracts, document remaining risks, independently review crypto/recovery design, and present evidence against every Phase 0 acceptance criterion. Do not implement application code or start Phase 1 without explicit authorization.

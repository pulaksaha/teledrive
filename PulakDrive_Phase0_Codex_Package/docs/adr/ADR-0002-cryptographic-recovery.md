# ADR-0002: Mandatory Recovery Kit with Supplementary Keychain

- Status: Accepted
- Decision date: 2026-11-11

## Context
A backup system is useful only if the user can recover data after losing the original Mac or Keychain.

## Decision
A user-managed recovery kit is mandatory before backup is enabled. macOS Keychain provides supplementary convenience but is not the only recovery mechanism. The recovery path must work on a clean environment without the original Mac's Keychain.

## Consequences
- Setup includes a recovery-kit export and verification ceremony.
- The recovery secret/document must never be uploaded to Telegram or logged. A separately encrypted VMK recovery-envelope ciphertext may be stored in a remote vault descriptor for clean-Mac recovery; the secret required to unwrap it remains user-held.
- Losing both usable local key material and the recovery kit may make data unrecoverable; the UX must explain this plainly.
- Exact format, entropy, encoding, and verification challenge are Phase 0 deliverables.

# ADR-0005: Telegram Is a Remote Replica, Not an Archival SLA

- Status: Accepted
- Decision date: 2026-11-11

## Context
The product uses a private Telegram channel as a convenient remote destination, but Telegram is not designed or promised as immutable backup storage.

## Decision
Treat Telegram as a best-effort remote replica/transport. Encrypt content and manifests before upload. Surface rate limits, account/session restrictions, missing objects, and degraded availability. Never assume remote messages are immutable or guaranteed to remain available.

## Consequences
- Recommend an independent backup destination for irreplaceable data.
- Build explicit restore verification and remote reconciliation.
- Do not silently propagate arbitrary Telegram-side deletion.
- Current API terms, limits, and account restrictions must be researched from official documentation in Phase 0, without connecting to an account.

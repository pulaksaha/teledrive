# ADR-0003: Indefinite Retention Until Manual Deletion

- Status: Accepted
- Decision date: 2026-11-11

## Context
Automatic age-based deletion risks irreversible data loss and conflicts with the product's recovery objective.

## Decision
Deleted files, tombstones, and historical versions are retained indefinitely until the user explicitly requests permanent deletion. There is no age-based garbage collection in the MVP. External Telegram deletion does not automatically propagate as a local deletion.

## Consequences
- Storage usage can grow without a time limit.
- The product must show storage usage and explain growth where measurable.
- Permanent purge requires authentication, an explicit confirmation, and a precise scope preview.
- Purge must account for manifests, versions, and all referenced chunks.
- Any future automatic retention policy requires a new ADR and explicit user approval.

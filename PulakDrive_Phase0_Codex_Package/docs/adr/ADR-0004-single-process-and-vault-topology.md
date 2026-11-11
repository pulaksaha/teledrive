# ADR-0004: One Python Service Process and One Mac per Vault

- Status: Accepted
- Decision date: 2026-11-11

## Context
Telethon session ownership and SQLite write coordination are simpler and safer with one service owner. Multi-device writers would require a distributed coordination and conflict protocol beyond MVP.

## Decision
Run one Python service process per user session. It owns SQLite writes and the sole Telethon client/session. MVP supports one Mac writer per vault.

## Consequences
- Avoid concurrent Telethon session use.
- Keep SQLite transactions short and service writes serialized.
- Design interfaces so future multi-device support is not impossible, but do not implement it in MVP.
- Service supervision must prevent duplicate instances.

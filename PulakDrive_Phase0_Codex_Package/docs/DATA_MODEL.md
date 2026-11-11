# Logical Data Model

This is a conceptual model for Phase 0 review. It is not a SQL schema.

## Entities

| Entity | Purpose | Key invariants |
|---|---|---|
| Vault | Logical encrypted backup namespace | Stable vault UUID; one active writer in MVP |
| KeyEnvelope | Wrapped VMK and recovery envelope metadata | Versioned format; no plaintext keys in DB |
| Root | User-selected folder root | Permission and identity tracked; path exposure minimized |
| FileEntry | Stable logical file identity | Not equivalent to a path; rename may preserve identity |
| FileVersion | Immutable snapshot of a file | Never mutate a committed version |
| Chunk | One encrypted application-level chunk | Unique version/index; ciphertext hash and size |
| RemoteObject | Telegram message/file reference | Opaque remote locator; may become unavailable |
| RemoteObjectBinding | Exclusive binding between one physical remote object and exactly one logical payload (chunk, manifest, or vault descriptor) | `remote_object_id` is the primary key; payload type and exactly one target identity must agree; all references are restrictive |
| Manifest | Encrypted catalog/commit record | References only verified uploaded chunks |
| Job | Durable operation | Idempotency key; resumable state machine |
| Conflict | Competing local/remote versions | Preserve both candidates |
| Tombstone | Logical deletion marker | Does not imply physical purge |
| EventCursor | Reconciliation progress | Watcher cursor is advisory; full scan can reset |
| AppSetting | Non-secret configuration | Secrets stay in Keychain or recovery mechanism |
| AuditEvent | Security/destructive-operation history | Redacted; no secrets or file contents |

## Important constraints

- Use foreign keys and migrations.
- Unique vault/generation, file-version, and version/chunk-index constraints.
- Keep SQLite transactions short.
- Persist job and chunk plan before remote side effects.
- Treat network operations as at-least-once and make them idempotent/reconcilable.
- A manifest is the commit record; an incomplete upload must not appear as a complete version.
- The selected logical proposal uses one common `RemoteObjectBinding` entity instead of three association tables. Each binding carries `payload_type` and exactly one target identity group: `(version_id, chunk_index)` for a chunk, `(vault_id, generation)` for a manifest, or `vault_id` for a descriptor. These target groups have matching foreign keys and restrictive deletion semantics; a consistency CHECK rejects partial/multiple groups, while triggers enforce `RemoteObject.kind` agreement and kind immutability after binding. Exact SQL/trigger bodies remain for a later reviewed migration.
- `remote_object_id` is the binding primary key, so one physical object can bind to only one payload and one category. Different remote IDs may bind to the same logical payload, allowing multiple copies.
- A chunk is remotely committed only with at least one confirmed chunk binding. A manifest is committed only after every referenced chunk is confirmed and the manifest itself has a confirmed manifest binding.
- Retain remote bindings and historical backup entities; no cascading delete. This is a logical proposal, not an executable schema or accepted implementation decision.
- A tombstone is recoverable metadata, not a deletion instruction.
- Historical versions remain indefinitely until explicitly purged.
- A purge must identify all manifests, chunks, and remote objects reachable from the selected scope.
- Store no plaintext cryptographic secrets or Telegram session credentials in SQLite.
- Document how schema migrations behave across crash/restart and app/service version mismatch.

## Phase 0 schema deliverable

Before Phase 1, produce:
1. ER diagram or equivalent relationship map.
2. State diagrams for Job, FileVersion, and Tombstone.
3. Migration and backup strategy for SQLite metadata.
4. Data classification table: plaintext locally, encrypted locally, encrypted remotely, secret-store only.
5. Retention/purge reachability rules.

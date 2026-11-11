# Telegram Storage Adapter Contract and Official Documentation Research

Research accessed 2026-11-11. Public documentation only; no Telegram connection, account, channel, credential, or session was accessed. Documentation is mutable; recheck before implementation/release.

## Boundary and transport-neutral interface

Only `telegram_adapter` may import Telethon or hold the MTProto session. Application layer sees opaque typed values, never Telethon classes:

```text
RemoteStore.inspect_configuration() -> StoreStatus
RemoteStore.list_candidate_channels() -> Sequence[ChannelCandidate]
RemoteStore.find_vault_descriptor(channel, vault_uuid) -> Sequence[DescriptorCandidate]
RemoteStore.put_object(object_id, encrypted_stream, size_hint, opaque_metadata, idempotency_key) -> PutReceipt
RemoteStore.get_object(locator, sink, expected_size_limit) -> GetReceipt
RemoteStore.find_by_idempotency_key(key) -> Optional[RemoteObject]
RemoteStore.refresh_locator(locator) -> RefreshedLocator
RemoteStore.delete_object(locator, explicit_purge_context) -> DeleteReceipt
RemoteStore.close() -> None
```

Conceptual, not final code contract. `put_object` accepts only already-encrypted bytes and opaque name; never plaintext paths or user metadata. `delete_object` is disabled unless a separately approved explicit purge job supplies authenticated scope and user-confirmation evidence. MVP default adapter exposes no automatic deletion path.

Clean-Mac recovery uses a user-selected dialog, not automatic selection. Telegram documents `messages.getDialogs` as returning the current user's dialog list, and Telethon 1.45 documents `iter_dialogs`/`get_dialogs`; message-history APIs exist. These public docs establish API availability, not that PulakDrive can safely enumerate every desired private channel/history under all account conditions. Before Phase 3, validate read-only pagination, visibility, and rate behavior through documentation and fake transport contracts. UI shows candidates, lets user select, locates descriptor by opaque vault UUID, authenticates its envelope, then requires user confirmation. On ambiguity/failure, stop; no channel creation or probe sends.

## Remote identity and ambiguous send

PulakDrive identity is a random opaque object UUID embedded in an encrypted/opaque envelope marker and local catalog, plus Telegram peer/channel identity and message ID as locator. Telegram message ID is not globally stable identity; file references can expire. Never use plaintext content hash as identifier. On ambiguous send, search/reconcile channel using opaque idempotency marker and compare expected encrypted digest/size before declaring success. If lookup is inconclusive, mark `needs_attention`; do not blindly resend or commit. Pagination and duplicate marker semantics must be specified before implementation.

## Error taxonomy

- `AUTH_REQUIRED`, `SESSION_REVOKED`, `CHANNEL_UNAVAILABLE`, `PERMISSION_DENIED`: pause and require user action; never retry login automatically.
- `RATE_LIMITED(retry_after)`: persist wait duration from Telegram/Telethon and pause; no tight-loop; user may cancel.
- `NETWORK_TRANSIENT`, `SERVER_TRANSIENT`: bounded exponential backoff with jitter and max retry policy; then visible paused/degraded state.
- `UPLOAD_PART_MISSING`, `UPLOAD_LIMIT_REJECTED`, `OBJECT_TOO_LARGE`: restart uncommitted object plan only after checking temp-part expiry/current account config; fail without manifest commit if size unsupported.
- `AMBIGUOUS_SEND`: reconcile by idempotency key before retry.
- `FILE_REFERENCE_EXPIRED/INVALID`: refetch source message/document metadata, refresh locator, retry same range; if unavailable return `REMOTE_OBJECT_MISSING`.
- `REMOTE_OBJECT_MISSING`, `REMOTE_INTEGRITY_MISMATCH`: degrade vault, preserve local/other versions, never infer deletion.
- `UNSUPPORTED_API`, `UNKNOWN_REMOTE_ERROR`: fail closed with sanitized diagnostics; no infinite retry.

No RPC while SQLite transaction is open. Network calls are bounded and cancellable. Initial concurrency at most one upload and one download subject to memory/disk budgets.

## Official documentation findings

Access date for every source below: **2026-11-11**.

| Source | Constraint/claim used |
|---|---|
| [Telegram Uploading and Downloading Files](https://core.telegram.org/api/files) | MTProto part-size constraints; 512 KiB recommended; dynamic part-count limits; `saveBigFilePart` above 10 MB; temporary upload-part lifetime is several minutes to hours; download reference errors and rate limits; file-hash support. |
| [Telegram Client Configuration](https://core.telegram.org/api/config) | `upload_max_fileparts_default` and premium counterpart are configuration values; size limit is dynamic. |
| [Telegram File References](https://core.telegram.org/api/file-references) | Expired/invalid references should be refreshed from source objects before retry. |
| [Telegram API Terms](https://core.telegram.org/api/terms) | Privacy obligations, own `api_id`, user disclosure and branding constraints. Requires product/legal review before distribution. |
| [Telegram Obtain API ID](https://core.telegram.org/api/obtaining_api_id) | Third-party app must obtain its own API ID before publication. |
| [Telethon 1.45 Session Files](https://docs.telethon.dev/en/stable/concepts/sessions.html) | Session file/string is sensitive and can authenticate account; protect it and revoke if compromised. |
| [Telethon 1.45 RPC Errors](https://docs.telethon.dev/en/stable/concepts/errors.html) | `FloodWaitError` provides wait seconds; unknown errors may map to generic RPC types; library behavior/version must be pinned and audited. |
| [Telethon 1.45 Client API](https://docs.telethon.dev/en/stable/modules/client.html) | `download_file` may return bytes when memory output selected; PulakDrive must use a sink/stream to bound memory. |
| [Telegram messages.getDialogs](https://core.telegram.org/method/messages.getDialogs) | Returns current user dialog list; method is user-only. Does not guarantee every channel is identifiable or history available. |
| [Telethon 1.45 dialog iteration](https://docs.telethon.dev/en/stable/modules/client.html) | `iter_dialogs`/`get_dialogs` lists dialogs; can take time and encounter FloodWait. |
| [Telethon 1.45 message retrieval](https://docs.telethon.dev/en/stable/modules/client.html) | Message retrieval methods exist; exact minimal read-only descriptor lookup flow must be verified before implementation. |

32 MiB is PulakDrive application chunk plaintext target, independent of MTProto part size. Validate ciphertext overhead and current account upload part limits before use. Dynamic limits/restrictions produce unsupported-size status, not silent architecture changes.

## Product/policy risk

Telegram API Terms require own `api_id`, privacy protection, and disclosure; naming/logo constraints also apply. Distribution/branding requires review. Telegram is not immutable storage and may become inaccessible through account restrictions, channel/message deletion, service changes, or rate limits. Encryption does not hide timing, approximate sizes, account/channel association, or access patterns.

## Approval boundary

Phase 0 research is public-doc-only. Phase 3 may implement adapter code under its phase authorization, but any live account/channel operation or real Telegram test additionally requires explicit user approval and a separate test procedure. Never ask user to paste credentials into Codex. Synthetic adapter tests use a fake transport.

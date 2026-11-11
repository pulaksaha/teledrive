# ADR-0006: LaunchAgent-Owned Service and Authenticated Loopback API

- Status: Accepted architecture direction; details in `docs/RUNTIME_AND_LOCAL_API.md` remain subject to security review.
- Decision date: 2026-11-11

## Context

The app needs login background operation while maintaining one Python process, one SQLite writer, and one Telethon session owner. Swift must not accidentally start a duplicate. A loopback API still crosses a trust boundary because local web origins and processes can issue requests.

## Decision

- A per-user LaunchAgent owns startup/restart of the single Python service.
- Swift shell discovers and authenticates to the existing service but never spawns or independently starts a Python process. User stop/restart/enable/disable uses supported Service Management/LaunchAgent controls; no raw PID signaling or shell commands.
- Service runs in the logged-in user's context and owns SQLite, sync, and Telethon.
- Service exposes authenticated, loopback-only, versioned API. Swift owns API requests and the long-lived per-install token, stored in Keychain and never exposed to React/JavaScript. The signed service may read the scoped Keychain item for validation. Host/Origin validation, native-session CSRF nonce, strict schemas, CSP/WKWebView navigation restrictions, and process/port identity validation are required.
- Disable/uninstall stops/unregisters LaunchAgent but does not delete vault or remote data.

## Alternatives considered

1. Swift launches service on demand: rejected because background operation and duplicate ownership are ambiguous.
2. Separate system LaunchDaemon: rejected for MVP due elevated privilege and Keychain-context risk.
3. Browser-only service: rejected by accepted native-shell ADR.

## Implications and remaining review

Token provisioning/rotation and embedded-web origin behavior need implementation-specific security review. Service version compatibility and DB migration sequencing must fail closed. Duplicate prevention, crash restart backoff, locked Keychain, logout/sleep/wake, update/uninstall require tests. No schema or encryption format changes are introduced.

LaunchAgent ownership and no-duplicate-shell rule are user-approved for this planning task. Exact Keychain access group, minimum macOS version, token bootstrap transport, and Origin/CSRF mechanism remain open for implementation review and may not be silently changed.

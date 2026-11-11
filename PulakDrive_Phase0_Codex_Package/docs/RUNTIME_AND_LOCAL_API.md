# Runtime Lifecycle and Local API Contract

Status: Phase 0 design contract. This document describes intended behavior; no service or API is implemented.

## Ownership and process model

- The per-user LaunchAgent exclusively executes and restarts the Python service. The native Swift shell discovers and communicates with the already-running instance. It never spawns a Python service; if the service is absent, report state and use only supported Service Management/LaunchAgent registration controls.
- Exactly one service instance per logged-in macOS user and vault installation. Enforce an OS-appropriate advisory lock held for process lifetime plus a runtime identity record. A stale identity file is not proof that the process is alive; validate process identity and authenticated health before acting. Never kill an unknown process solely because a port or PID file is stale.
- The Python service owns SQLite connections, sync coordinator, and sole Telethon client/session. Shutdown stops accepting new work, persists resumable job state, disconnects Telethon, closes DB resources, and releases the lock.
- Use a per-user LaunchAgent, not a system LaunchDaemon. Register/unregister through supported Service Management integration. Minimum supported macOS version and fallback behavior remain release-target decisions.

## Lifecycle

1. Installer places signed shell/service resources in an immutable app bundle and records installation identity and compatible protocol versions.
2. During setup, shell asks user to enable background operation. Registration status and disablement are visible; never silently re-register against the user's choice.
3. At login, launchd starts the service in the logged-in user context. Service takes its lock, validates/migrates the DB before serving, initializes Keychain access, then publishes a ready health record.
4. Shell locates and authenticates to service. It never launches a second copy. If no ready service exists, distinguish disabled, starting, incompatible, locked, failed, and stale states.
5. On logout, OS shutdown, or requested stop, service stops accepting jobs and exits cleanly. Jobs remain durable and resumable. Sleep pauses network work as needed; wake revalidates connectivity, auth state, and file stability before resuming.
6. launchd may restart a crashed service with bounded backoff. Repeated failure becomes visible and must not cause an uncontrolled restart loop. User stop/restart requests go through supported Service Management/LaunchAgent controls; no `Process`, subprocess, direct PID signal, shell command, or independent Python launch from Swift.
7. Update installs the new signed bundle, validates shell/service protocol compatibility, takes a pre-migration DB snapshot, then allows the new service version to start. Failed migration leaves service unavailable and preserves the snapshot; it must not silently run an incompatible version.
8. Uninstall disables/unregisters LaunchAgent through supported Service Management controls and stops service. It does not delete vault data, DB, Keychain items, sessions, or remote Telegram data unless separately selected and explicitly confirmed with a scope preview.

## Local API/IPC

MVP uses authenticated HTTP bound only to IPv4 loopback and IPv6 loopback where supported. No LAN or wildcard listener. Unix-domain socket remains an alternative only through an ADR; API contract must not depend on a chosen port.

### Native-owned authentication and React bridge

- Generate 256 bits from OS CSPRNG at first install/setup. Store only in per-user Keychain, accessible to the signed Swift shell and signed service via a narrowly scoped access group. The service may load its expected token from Keychain into protected process memory; neither token nor derived verifier is stored in SQLite.
- Swift is the only API client for WKWebView-originated UI actions: React sends narrowly typed `WKScriptMessageHandler` commands to Swift; Swift validates the command/schema and issues a URLSession request with Authorization header. Never expose the long-lived token, API base URL, generic HTTP method, or arbitrary endpoint proxy to JavaScript. No bearer token in URLs, browser storage, logs, crash reports, command line, or environment.
- Native bridge exposes an allowlist of named operations with bounded argument schemas (for example, status, list jobs, pause job, request restore preview). It must not expose arbitrary API fetch, shell, filesystem path, or Telegram methods. Destructive/purge operations require native confirmation with exact scope preview.
- Provisioning is local: Swift creates/stores token in Keychain; service retrieves same scoped Keychain item after its LaunchAgent-owned startup; an authenticated handshake confirms both sides. If actual signing/access-group constraints prevent this, stop and propose an ADR rather than send token via argv, environment, or SQLite.
- Rotation is initiated by native Swift: create/store replacement in Keychain; service reloads through protected Keychain access; verify, then invalidate old token. Any overlap is short and time-bounded. Partial rotation fails closed and requires local re-provisioning; never write token to DB.
- Missing/locked Keychain item disables authenticated API access and pauses sensitive actions; never generate a replacement silently.
- Missing/locked Keychain item disables authenticated API access and pauses sensitive actions; never generate a replacement silently.

### Origin, Host, CSRF, and request rules

- Trusted WKWebView root is proposed as `pulakdrive://ui/`; its origin tuple is `pulakdrive://ui`. Verify actual origin serialization for the selected WKWebView scheme during implementation review; if it serializes as opaque/null, do not weaken checks or allow all null origins—revise scheme via ADR. Swift's explicit HTTP `Origin` marker is defense-in-depth metadata, not proof of caller identity.
- WKWebView loads only signed bundled UI assets for the trusted origin. Deny external top-level navigation, redirects, popups, frames, downloads, and remote subresources; disable file URL access/universal file access. External links, if product later permits them, open outside WKWebView after an explicit native action.
- For every script message, Swift verifies it came from the main frame, the exact trusted security origin, the expected content world, and an allowlisted message name/schema. Reject all other frames/origins and stale UI-session messages.
- Apply restrictive CSP from trusted local resources: `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-src 'none'`. No inline script/eval unless separately justified and reviewed. Add web-content process isolation and content blockers where available.
- Validate Host against exact numeric loopback address and selected port; reject DNS names, public/interface addresses, malformed authority, and forwarded headers. Native URLSession sets exact expected Origin marker and a native per-session CSRF nonce; server accepts only the configured trusted origin plus valid bearer token and nonce. Browser requests without token/nonce fail; CORS is disabled (no wildcard).
- Do not use cookies for API authentication. Since JavaScript cannot attach the native-held bearer or anti-CSRF nonce, browser-based CSRF is blocked by design. The native session nonce is defense in depth and remains in Swift/service memory, never exposed to JS. Origin/Host are not authentication and can be forged by non-browser processes; bearer authentication remains mandatory.
- Apply schema validation, request/body limits, timeouts, content-type checks, and stable versioned error codes. Avoid reflecting untrusted values.
- No arbitrary shell, SQL, Telethon, or filesystem-path endpoint. UI references registered roots and opaque IDs.
- State-changing operations require authentication and authorization. Long transfers create durable jobs and return job IDs.

### Port discovery and stale processes

- Service binds an available loopback port, then atomically publishes a small runtime record under a user-private runtime directory: protocol version, port, PID, process-start identity, installation ID, and random instance ID. No token/secret in this record.
- Create record with restrictive permissions and atomic replacement. Shell validates owner/mode, verifies process identity and authenticated health, and refuses to trust PID/port alone.
- On shutdown remove only the record matching current instance ID. If stale, shell may use supported Service Management/LaunchAgent registration/restart controls, then rediscover; it must not spawn, signal arbitrary PIDs, or trust a stale record.
- Consider socket activation/reserved port only if dynamic discovery proves insufficient; no additional backend process.

### Version compatibility

- API has explicit major/minor protocol version and capability negotiation. Incompatible major versions fail closed with clear upgrade/restart message.
- Minor versions are additive only. Unknown optional response fields are ignored; unknown request fields are rejected unless explicitly declared extensible.
- Shell/service ship as one signed bundle. Service validates installed bundle/build identity; rollback is allowed only when DB schema compatibility is declared and migration has not irreversibly advanced.
- These controls require implementation tests; this contract is not test evidence.

## Open implementation review items

Implementation-specific security review is required for shared Keychain access group, token reload/rotation, actual custom-scheme origin behavior, `WKScriptMessageHandler` exposure, CSP enforcement, service authentication middleware, and Service Management APIs/minimum macOS release. Threat model excludes malware already running as the same user; document this limit. If same-user compromise is in scope, redesign with stronger OS isolation before implementation.

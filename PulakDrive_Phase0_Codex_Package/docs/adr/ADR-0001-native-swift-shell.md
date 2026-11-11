# ADR-0001: Native Swift macOS Application Shell

- Status: Accepted
- Decision date: 2026-11-11

## Context
PulakDrive needs reliable macOS lifecycle integration, background startup, permissions, notifications, and secure local capability access while retaining a productive web UI.

## Decision
Use a native Swift macOS shell. Present the React + TypeScript interface inside a controlled native web view. The Python service remains the single core service process. Use a narrow allowlisted native bridge for typed UI commands and Keychain operations; do not expose arbitrary native APIs, generic API proxying, or the long-lived service bearer token to web content. The shell manages LaunchAgent registration and communicates with the existing service but never spawns a Python process.

## Consequences
- Better alignment with macOS lifecycle and Keychain.
- Additional packaging, signing, and Swift maintenance.
- UI/service contract must remain explicit and versioned.
- The per-user LaunchAgent exclusively owns service startup/restart; the Swift shell only manages supported registration controls and discovers/communicates with the existing instance. See ADR-0006 and `RUNTIME_AND_LOCAL_API.md`.

## Alternatives considered
- Browser-only local portal: simpler, but weaker native lifecycle and capability integration.
- Tauri: viable cross-platform shell, but not selected for this Mac-first product.

// PulakDrive macOS application shell entry point (Phase 1 skeleton)
//
// IMPORTANT — BLOCKED FEATURES:
// - WKWebView bridge: blocked until origin serialization and security review are complete.
// - Keychain integration: blocked until API/token security review is complete.
// - LaunchAgent registration: blocked until Service Management/signing review is complete.
// - Production bearer token: blocked.
// - Real Python service IPC: blocked.
//
// This entry point compiles and exits cleanly for CI verification purposes.
// It does not start a service, access Keychain, or perform network operations.

import Foundation
import PulakDriveLib

// Phase 1 Milestone 1: foundation skeleton only.
// Real application lifecycle (AppDelegate, NSApplication, WKWebView) is
// deferred until the WKWebView origin/bridge security review is complete.
//
// For now, this target exists to verify the Swift package compiles cleanly.
let status = AppStatus.mockNotConfigured
print("PulakDrive foundation — Phase 1 Milestone 1 (skeleton)")
print("Service state: \(status.serviceState)")
print("Vault state: \(status.vaultState)")
print("Note: real application lifecycle is deferred to Milestone 2.")

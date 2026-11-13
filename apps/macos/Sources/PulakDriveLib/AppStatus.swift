import Foundation

/// ServiceState represents the observable lifecycle state of the PulakDrive Python service.
///
/// This model is used only for UI presentation. No authentication, cryptographic operations,
/// or Keychain access are performed in Phase 1. Those are blocked until the relevant
/// security review milestones are complete.
public enum ServiceState: String, Sendable, CustomStringConvertible {
    /// Service has not been configured or discovered yet.
    case notConfigured
    /// Service process is starting up.
    case initializing
    /// Service is running and healthy.
    case ready
    /// Service is paused by the user.
    case paused
    /// Service is running but in a degraded state (e.g., connectivity issues).
    case degraded
    /// Service requires user attention (e.g., configuration needed).
    case needsAttention
    /// Service process is not reachable.
    case serviceUnavailable

    public var description: String { rawValue }
}

/// VaultState represents the lifecycle state of the local vault.
///
/// Phase 1 foundation: values are not persisted to SQLite in this milestone.
/// SQLite schema decisions are still being finalized (Milestone 4 prerequisite).
public enum VaultState: String, Sendable, CustomStringConvertible {
    /// No vault exists on disk.
    case noVault
    /// Vault is being initialized.
    case initializing
    /// Vault is ready for backup operations.
    case ready
    /// Vault is locked (e.g., key unavailable).
    case locked
    /// Vault metadata is potentially corrupted.
    case degraded

    public var description: String { rawValue }
}

/// AppStatus is the top-level observable state surfaced to the UI.
///
/// This is mock data for Milestone 1. No real service or vault is queried.
public struct AppStatus: Sendable {
    public let serviceState: ServiceState
    public let vaultState: VaultState
    public let lastSuccessfulBackup: Date?
    public let filesIndexed: Int
    public let pendingJobs: Int
    public let failedJobs: Int

    public init(
        serviceState: ServiceState,
        vaultState: VaultState,
        lastSuccessfulBackup: Date? = nil,
        filesIndexed: Int = 0,
        pendingJobs: Int = 0,
        failedJobs: Int = 0
    ) {
        self.serviceState = serviceState
        self.vaultState = vaultState
        self.lastSuccessfulBackup = lastSuccessfulBackup
        self.filesIndexed = filesIndexed
        self.pendingJobs = pendingJobs
        self.failedJobs = failedJobs
    }

    /// A safe mock status for use in tests and UI previews.
    /// Does not reflect a real backup state.
    public static var mockNotConfigured: AppStatus {
        AppStatus(serviceState: .notConfigured, vaultState: .noVault)
    }
}

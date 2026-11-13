// PulakDriveTests — Pure Swift test suite (no XCTest dependency)
// Uses Swift Testing framework (available since Swift 5.9 / Xcode 15).
// Runs with: swift test
//
// XCTest is intentionally not used here because the development environment
// uses Command Line Tools only (no full Xcode.app), where XCTest is unavailable.
// Swift Testing works with the Swift package manager's built-in test runner.

import Foundation
import Testing
@testable import PulakDriveLib

// MARK: - ServiceState tests

@Suite("ServiceState")
struct ServiceStateTests {
    @Test("All cases have non-empty description")
    func allCasesHaveNonEmptyDescription() {
        let cases: [ServiceState] = [
            .notConfigured, .initializing, .ready, .paused,
            .degraded, .needsAttention, .serviceUnavailable
        ]
        for state in cases {
            #expect(!state.description.isEmpty)
        }
    }

    @Test("rawValue matches description")
    func rawValueMatchesDescription() {
        #expect(ServiceState.notConfigured.description == "notConfigured")
        #expect(ServiceState.serviceUnavailable.description == "serviceUnavailable")
        #expect(ServiceState.degraded.description == "degraded")
    }
}

// MARK: - VaultState tests

@Suite("VaultState")
struct VaultStateTests {
    @Test("All cases have non-empty description")
    func allCasesHaveNonEmptyDescription() {
        let cases: [VaultState] = [.noVault, .initializing, .ready, .locked, .degraded]
        for state in cases {
            #expect(!state.description.isEmpty)
        }
    }
}

// MARK: - AppStatus tests

@Suite("AppStatus")
struct AppStatusTests {
    @Test("mockNotConfigured has correct states")
    func mockNotConfiguredHasCorrectStates() {
        let status = AppStatus.mockNotConfigured
        #expect(status.serviceState == .notConfigured)
        #expect(status.vaultState == .noVault)
        // Must never falsely show a successful backup
        #expect(status.lastSuccessfulBackup == nil)
        #expect(status.filesIndexed == 0)
        #expect(status.pendingJobs == 0)
        #expect(status.failedJobs == 0)
    }

    @Test("init sets all fields correctly")
    func initSetsAllFields() {
        let date = Date(timeIntervalSince1970: 1_000_000)
        let status = AppStatus(
            serviceState: .ready,
            vaultState: .ready,
            lastSuccessfulBackup: date,
            filesIndexed: 42,
            pendingJobs: 3,
            failedJobs: 1
        )
        #expect(status.serviceState == .ready)
        #expect(status.vaultState == .ready)
        #expect(status.lastSuccessfulBackup == date)
        #expect(status.filesIndexed == 42)
        #expect(status.pendingJobs == 3)
        #expect(status.failedJobs == 1)
    }

    @Test("Mock data must not falsely claim backup success")
    func noFalseSuccessInMockData() {
        let status = AppStatus.mockNotConfigured
        #expect(status.lastSuccessfulBackup == nil,
                "Mock 'notConfigured' must not report a successful backup")
    }
}

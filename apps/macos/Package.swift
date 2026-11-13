// swift-tools-version:5.10
// PulakDrive — macOS application shell (Phase 1 foundation skeleton)
// No production crypto, Keychain, or LaunchAgent integration yet.
// Those are blocked pending security review milestones.

import PackageDescription

let package = Package(
    name: "PulakDrive",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "PulakDrive", targets: ["PulakDrive"]),
        .library(name: "PulakDriveLib", targets: ["PulakDriveLib"])
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "PulakDrive",
            dependencies: ["PulakDriveLib"],
            path: "Sources/PulakDrive"
        ),
        // Shared library of testable domain types — no executable code.
        .target(
            name: "PulakDriveLib",
            dependencies: [],
            path: "Sources/PulakDriveLib"
        ),
        .testTarget(
            name: "PulakDriveTests",
            dependencies: ["PulakDriveLib"],
            path: "Tests/PulakDriveTests"
        )
    ]
)

# JourneyCore: a complete portable Swift package

This project accompanies swift-026, swift-027 and swift-039 through swift-048. It contains a real library target, executable target and XCTest target. It has no external package dependencies. Use a prepared Swift 6 toolchain on Linux or macOS. Windows learners use their prepared Linux environment through WSL 2 and Docker.

Copy this directory to your own ignored learning workspace before edits. From the copied package directory:

```bash
swift --version
swift build
swift test
swift run journey-demo
```

Expect four XCTest methods to pass and the executable to print `JourneyCore: 1/2 complete; round trip passed`. Build creates `.build` only inside the copied package. `swift package clean` removes its build products, not your source. Do not run broad filesystem cleanup.

`StudyItem` represents stable identity and editable data. `StudyPlan` admits unique identities, preserves value snapshots and retains schema version 1. Decoding validates again because synthesized Codable does not call the public validating initializer. `update` validates its replacement before changing the stored array. `add` validates a candidate copy, so rejected duplicates leave the old plan intact.

The tests intentionally reject plausible defects: shared mutation, duplicate identity admission, missing post-decode validation and partial state change after an invalid edit. Add cases for a new feature before changing its contract. A successful package test does not prove the Apple UI rendered, a device installed the app or a saved file survived a process crash.

The adjacent JourneyApp project uses this package as a local dependency. Keep both directories adjacent when copying the app lab. The core has no SwiftUI dependency and is the portable testing seam for future applications.

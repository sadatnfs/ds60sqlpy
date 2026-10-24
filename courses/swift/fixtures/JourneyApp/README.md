# JourneyApp: a complete offline SwiftUI project lab

This project supplies actual SwiftUI app source, an observable model, validated local-package domain code, navigation, editing, recoverable JSON persistence, UIKit/AppKit text bridges and an XCUITest smoke test. Its reviewed `project.yml` generates two real targets: JourneyMac and JourneyIOS. It is separate from the Linux classroom pad. Linux executes the portable chapter kernels and JourneyCore, not SwiftUI, UIKit, simulators or signing.

## Prepare deliberately on macOS

Use a supported Xcode installation with Swift 6 support and an installed iOS simulator if following the iOS path. Open Xcode once to finish its required setup. XcodeGen 2.42 or newer generates the project from the checked-in specification. If you choose Homebrew as your existing package manager, preparation is:

```bash
brew install xcodegen
xcodebuild -version
xcodegen --version
```

This installation needs network access during preparation. Reading the lesson or running the Linux pad does not install XcodeGen. Consult the [XcodeGen project specification](https://github.com/yonaskolb/XcodeGen/blob/master/Docs/ProjectSpec.md) for generator behavior.

Copy both `JourneyApp` and adjacent `JourneyCore` into your own ignored learning directory, preserving their relative locations. Work in your copy. First run `swift test` in JourneyCore, then from JourneyApp:

```bash
xcodegen generate --spec project.yml
xcodebuild -list -project JourneyApp.xcodeproj
xcodebuild -showdestinations -project JourneyApp.xcodeproj -scheme JourneyMac
xcodebuild -project JourneyApp.xcodeproj -scheme JourneyMac -destination 'platform=macOS' CODE_SIGNING_ALLOWED=NO build
open JourneyApp.xcodeproj
```

The first compile intentionally disables signing for a local build check. In Xcode, select JourneyMac and My Mac, then Run. For iOS, select JourneyIOS and an installed simulator. Use `xcodebuild -showdestinations -project JourneyApp.xcodeproj -scheme JourneyIOS` to inspect actual destinations. Do not copy an invented simulator identifier from an unrelated machine.

The project has no third-party package downloads: JourneyCore is a local dependency. XcodeGen is a preparation tool. Personal development teams, certificates and provisioning profiles are intentionally absent. Configure your own team locally only when device installation or distribution requires it. Do not commit that identity or signing assets.

## What to inspect

1. Add a nonempty item and observe the progress count.
2. Open it, edit its title, mark it complete and save. Identity remains stable.
3. Open it again, modify the draft and cancel. The saved model remains unchanged.
4. Quit and relaunch. The saved plan is restored from the app-owned application support directory.
5. Open the app using keyboard navigation and VoiceOver. Each row speaks title and completion without relying on color. Check large text, long titles, reduced motion and both appearances.
6. Inspect the selectable text adapter on each Apple platform you actually run. Conditional compilation is not evidence for an untested platform.

`PlanStore` saves only to `JourneyLearningFixture/plan.json` beneath the app's application support directory. The exact container path depends on the platform. If decoding or validation fails, the original file is retained and automatic writes are blocked. The UI reports the failure. Back up the file before manually repairing or replacing it in an owned test environment. Do not use a learner's only saved copy to test corruption.

The app uses a small synchronous local save for clarity. A larger app should move heavy I/O to an owned adapter while preserving MainActor presentation state, request identity and failure accounting. Add networking behind a protocol; on Linux an actual URLSession implementation imports FoundationNetworking explicitly. Check HTTP status, bounded response size, decoding, domain validation and cancellation. No network request is part of the default app.

## Test the actual Apple UI

The supplied UI test launches with `--ui-testing`, which gives it fixed fixture state and a separate temporary save directory. It never resets the normal application support file. On a prepared Mac with Xcode's UI-testing permission enabled:

```bash
xcodebuild -project JourneyApp.xcodeproj -scheme JourneyMac -destination 'platform=macOS' test
```

For iOS, use an actual installed simulator destination from `-showdestinations` and the JourneyIOS scheme. Record the Xcode version, scheme, destination, result and any signing or permission limitation. A simulator pass does not prove physical-device installation, accessibility inspection or App Store distribution.

## Extend without breaking ownership

The deliberate flow is view action, model operation, validated candidate value, file write, then published state. A failed write leaves the previous in-memory plan intact. The editor has a temporary draft for explicit Save and Cancel semantics. A future live editor needs a different binding contract rather than silently changing that behavior.

Try adding due dates, filtered views or a version-two schema. Write domain tests first, preserve old saved data through an explicit migration, and then add UI evidence. Keep a small table separating portable tests, package builds, macOS UI, iOS simulator, physical device and signing. Mark surfaces that have not actually run.

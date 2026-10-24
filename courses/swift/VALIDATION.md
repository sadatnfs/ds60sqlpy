# Swift validation scope

All 48 published portable references passed the actual `execute_operation` worker path with `isolate_user=True` in the prepared Swift 6.3.3 Linux ARM64 image. The checks used the original bounded worker limits, no network, a read-only image and temporary disposable state. Each input hash was compared with its published reference. The explicit @main wrapper and strict Swift 6 compile mode were used throughout.

The complete JourneyCore package built under the same Swift image in a separate disposable project workspace. All four XCTest methods passed, and the journey-demo executable passed its round-trip and completion checks. This package workflow has its own build storage requirement and is not a project-upload feature of the single-file pad.

The JourneyApp source and XcodeGen specification provide actual macOS and iOS application targets, local package integration, navigation, editing, recoverable persistence, UIKit/AppKit adapters and a UI test. Apple UI execution, simulator/device behavior, accessibility inspection and signing have not been established by the Linux checks. Follow its README on a prepared Mac with Xcode and record those observations separately. A host containing only command-line tools may lack the XCTest and app-development surfaces needed for these Apple project steps.

The authoring pipeline regenerated all 194 track, manifest and lesson artifacts without drift. Its Python sources pass scoped lint and format checks, and shared catalog admission recognizes all 48 lessons. These results do not promise every architecture, every engine installation or the absence of undiscovered defects. Browser delivery and repository release CI remain distinct gates.

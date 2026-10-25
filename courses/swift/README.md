# Swift: a complete language learning journey

From the repository root, prepare this worker with:

```bash
./classroom --profile swift-linux
```

Choose the subject from **All learning paths**. The [setup guide](../../docs/one-command-classroom.md)
explains Docker on macOS, Linux and Windows WSL 2. Use `./classroom stop` and
`./classroom resume` with the same project to retain your source, notes and
results. An explicit profile list replaces the saved runtime selection while
preserving work in its named volume.

This path contains 48 practice chapters, with sixteen beginner, sixteen intermediate and sixteen advanced chapters. Open the unified Docker classroom, choose Swift, and move at your own pace. The stable lesson IDs preserve separate saved pads, notes and progress. Follow prerequisites when a mechanism is unfamiliar rather than treating the minute estimates as deadlines.

Each chapter explains vocabulary and syntax, walks through two complete examples, asks six progressive tasks and keeps its unfinished starter separate from executable references and explanatory solutions. A success marker demonstrates the checked fixture ran; independent explanation and transfer remain part of learning.

The prepared `swift-linux` worker compiles a single saved source file. It does not accept arbitrary command arguments, stdin, package installation or multi-file project uploads. All ordinary references are deterministic and offline after image preparation. Source compilation, runtime execution, browser delivery and external project evidence are separate checks.

The Swift route teaches Swift 6 language mechanisms, Unicode, optionals, value/reference semantics, protocols, generics, ARC, Codable, packages, testing, structured concurrency, actors, Sendable, streams, performance and app architecture. The worker uses an explicit @main entrypoint with a fixed Swift 6 compile contract.

Linux Docker runs portable Swift and Foundation examples. SwiftUI, UIKit, AppKit, Apple simulators and app signing require macOS and Xcode in separately prepared project labs. The complete [JourneyCore](fixtures/JourneyCore/README.md) package supplies a portable library, executable and tests. The complete [JourneyApp](fixtures/JourneyApp/README.md) supplies real SwiftUI source, XcodeGen project specification, local package integration, navigation, editing, persistence, platform bridges and UI tests. Apple GUI execution is never claimed from Linux evidence.

The maintained route is [track.json](track.json) and authored admission is [lessons.json](lessons.json). Contributors should read [AGENTS.md](AGENTS.md) and [authoring instructions](authoring/README.md). Lesson estimates support planning; a finite course cannot promise expertise in every future library or production environment.

See [validation scope](VALIDATION.md) for the distinction between executed portable references and separately prepared project surfaces.

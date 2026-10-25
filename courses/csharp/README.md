# C#: a complete language learning journey

From the repository root, prepare this worker with:

```bash
./classroom --profile csharp-dotnet
```

Choose the subject from **All learning paths**. The [setup guide](../../docs/one-command-classroom.md)
explains Docker on macOS, Linux and Windows WSL 2. Use `./classroom stop` and
`./classroom resume` with the same project to retain your source, notes and
results. An explicit profile list replaces the saved runtime selection while
preserving work in its named volume.

This path contains 48 practice chapters, with sixteen beginner, sixteen intermediate and sixteen advanced chapters. Open the unified Docker classroom, choose C#, and move at your own pace. The stable lesson IDs preserve separate saved pads, notes and progress. Follow prerequisites when a mechanism is unfamiliar rather than treating the minute estimates as deadlines.

Each chapter explains vocabulary and syntax, walks through two complete examples, asks six progressive tasks and keeps its unfinished starter separate from executable references and explanatory solutions. A success marker demonstrates the checked fixture ran; independent explanation and transfer remain part of learning.

The prepared `csharp-dotnet` worker compiles a single saved source file. It does not accept arbitrary command arguments, stdin, package installation or multi-file project uploads. All ordinary references are deterministic and offline after image preparation. Source compilation, runtime execution, browser delivery and external project evidence are separate checks.

The C# route teaches .NET 10 and compatible C# 14, from source and values through collections, nullability, records, interfaces, LINQ, resource ownership, JSON, asynchronous work, cancellation, channels, locks, memory, HTTP, API architecture, security and deployment. The fixed project uses framework libraries and no NuGet packages.

The complete [DomainLab](fixtures/DomainLab/README.md) and [ApiLab](fixtures/ApiLab/README.md) teach multi-project composition and a real local ASP.NET Core server outside the single-file pad. Their READMEs give exact commands, expected observations and cleanup boundaries.

The maintained route is [track.json](track.json) and authored admission is [lessons.json](lessons.json). Contributors should read [AGENTS.md](AGENTS.md) and [authoring instructions](authoring/README.md). Lesson estimates support planning; a finite course cannot promise expertise in every future library or production environment.

See [validation scope](VALIDATION.md) for the distinction between executed portable references and separately prepared project surfaces.

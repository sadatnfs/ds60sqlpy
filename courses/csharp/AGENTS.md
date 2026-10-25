# C# course ownership

Read the root AGENTS.md and the add-learning-path skill before changes. This subject has 48 stable IDs in three stages. Preserve IDs, prerequisite relationships, learner pads and solution paths.

The durable specifications are in authoring/foundations.py, composition.py and advanced.py. Edit these before generated guides or solutions. Run `python courses/csharp/authoring/build.py` from the repository root. The generator writes UTF-8 with LF and never touches another subject or generated HTML.

The ordinary profile is `csharp-dotnet`. Keep all reference programs deterministic, bounded and offline, with always-active failure checks. The classroom accepts one source file, not arbitrary project files, package installation, command arguments or stdin. External project fixtures have their own explicit preparation and platform boundaries.

Each practice chapter needs original mechanism teaching, vocabulary, two complete worked examples, six progressive tasks, diagnosed mistakes, an answer-free starter and a separate executable/explanatory solution. Do not use em dashes or generic topic-list filler. Do not suppress failed assertions or claim production readiness from compilation alone.

The `csharp-dotnet` worker stages `Program.cs` in a fixed .NET 10 console project.
Ordinary examples use prepared framework libraries without ad hoc NuGet packages.
ASP.NET and multi-file application fixtures have a separate explicit project
workflow; a successful console program does not qualify an HTTP service.

Run subject generation drift checks, compiler/reference checks in the actual prepared worker, module and rendering validation, and project-specific checks. Record skipped platforms honestly. Root integration owns shared loaders, workers, themes and CI.

Use [the subject authoring guide](authoring/README.md) for regeneration and
[the module contract](../../docs/implementation/ADDING_A_MODULE.md) for shared
runtime integration. Root guidance owns common formatting, saved-work and
publication rules; subject changes must preserve those boundaries.

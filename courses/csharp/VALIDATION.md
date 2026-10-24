# C# validation scope

The initial implementation contains 48 complete, separately compiled reference programs. All 48 have compiled and executed successfully in the prepared .NET 10 Linux ARM64 image with an unprivileged learner identity, no network, a read-only image, bounded temporary storage, process count, memory and CPU. Assertions throw on failure and remain active in ordinary builds. Reference input hashes were compared with the published source.

Compiler diagnosis identified a Roslyn failure caused by a 32 MiB descriptor file-size limit, reported misleadingly as out of memory. A 64 MiB limit for compilation passed, while the runtime phase retained 32 MiB. This diagnostic evidence is separate from final integrated worker and browser acceptance; the trusted backend owns that phase-specific policy.

The actual DomainLab two-project fixture built and passed seven checks. The actual ApiLab built, started on an owned loopback endpoint inside an ephemeral container, and passed six status scenarios: health 200, creation 201, lookup 200, duplicate 409, invalid input 400 and missing item 404. The server stopped and its disposable container was removed. No learner volume was mounted or modified.

The authoring pipeline regenerated all 194 track, manifest and lesson artifacts without drift. Its Python sources pass the repository's scoped lint and format checks. Shared catalog admission recognizes all 48 lessons. These checks do not establish every architecture, every external SDK installation, durable production storage, authentication or the absence of undiscovered defects. Browser delivery and release CI remain separate repository-wide gates.

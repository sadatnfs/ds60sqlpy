# C++ authoring rules

Read [root guidance](../../AGENTS.md), the [content contract](../../docs/content-authoring.md)
and [module integration](../../docs/implementation/ADDING_A_MODULE.md).
Preserve stable IDs and prerequisites. Keep guides, learner source, executable
references and explanations aligned. Each practice guide defines vocabulary,
explains syntax, gives at least two bounded worked examples, and includes six
inspectable exercises, progressive hints, retrieval and a lesson-specific
`Ask an AI tutor about this lesson` prompt. A reference run is not proof of
learner understanding.

Register complete bundles through `lessons.json`. Keep `verification_id` null
unless its trusted typed verifier is registered and tested. Content metadata
cannot install tools or execute arbitrary commands. Preserve learner state,
reviewed fixtures and private runtime credentials. Update durable authoring
sources where present, then regenerate and run focused content/runtime checks.
Do not use em dashes.

Teach source, compilation, linking, entrypoints and diagnostics before larger
programs. The `cpp20` worker stages `main.cpp`. Explain C++20 version choices,
value/reference semantics, lifetime, RAII, ownership, undefined behavior,
exception guarantees and concurrency as those mechanisms appear. Do not assume
external libraries or a multi-file build in the single pad. Larger fixture
projects need their separately documented build path.

Use deterministic examples with boundary cases. A compiler success does not
establish lifetime safety or correct behavior. Test references and plausible
wrong implementations in the prepared worker, including compile errors and
bounded execution. Fixtures and verifier harnesses remain reviewed inputs;
learner source must not choose or replace the oracle.

The [depth authoring guide](authoring/depth/README.md) owns generated worked
examples and marked explanatory regions. Preserve directly authored base guides,
learner/reference programs and fixture projects outside that scope. CUDA C++ is
a separate [GPU subject](../cuda/README.md); an ordinary C++20 compiler does not
provide device execution. Keep CMake/install projects and one-file pad acceptance
as separate evidence.

# Java authoring rules

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

Explain source, bytecode, the JVM, compilation and runtime errors separately.
The `java21` worker stages `Main.java`, uses public class `Main` without a package
declaration, and enables assertions. Helper classes may share that file.
Multi-file projects and external dependencies need their own documented build
path; do not assume Maven or extra libraries in a single coding pad.

Teach value/reference behavior, generics, collection contracts, exceptions,
resource ownership, concurrency and memory visibility with observable examples.
Advanced lessons should compare alternatives and diagnose failures, not only
introduce APIs. Test invalid and boundary inputs in the prepared Java runtime.

Existing bundles and project fixtures are maintained directly unless a specific
authoring tool explicitly owns them. Preserve prepared H2 JDBC fixtures and
teach their database behavior as H2, not PostgreSQL. Inherited JVM resource
settings and diagnostic stderr are part of the worker contract. Review the
[classroom module contract](../../docs/implementation/ADDING_A_MODULE.md) before
changing entrypoints, dependencies or multi-file expectations.

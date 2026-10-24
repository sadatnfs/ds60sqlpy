# JavaScript and TypeScript authoring rules

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

Keep Node and browser environments distinct. The Node worker stages `main.mjs`;
TypeScript stages `main.mts`, performs strict NodeNext checking and compiles
before Node execution. Use only prepared built-ins and declared typings. Do not
install packages from a normal example. Browser DOM APIs such as `document` and
`window` require the documented browser fixture route or reading mode.

Explain coercion, scope, closures, object identity, modules, asynchronous jobs,
errors and runtime validation before large applications. Types do not validate
external data at runtime. Teach cancellation, resource cleanup and failure
paths. Preserve the authoring specifications and browser fixture separation;
execute browser behavior in a real browser when it is part of the claim.

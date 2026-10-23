# Scala and Apache Spark authoring rules

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

Teach Scala values, types, functions and collections before distributed jobs.
The JVM route stages `Main.scala` with `object Main`; PySpark variants stage
`main.py`. Keep canonical IDs and variant aliases stable so each implementation
retains its own saved source and jobs. Match the prepared Scala, JVM and Spark
versions rather than host installations.

Explain schema, row grain, lazy evaluation, partitions, shuffles, ordering,
null semantics and driver/executor behavior. Use small local datasets and bound
collects. Start and stop Spark sessions explicitly. Compare Scala and PySpark
semantics without counting variants as separate canonical learning objectives.
A local test does not prove distributed scale or production fault recovery.

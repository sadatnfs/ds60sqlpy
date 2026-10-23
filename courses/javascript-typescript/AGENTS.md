# Language authoring contract

Read the root AGENTS.md, docs/content-authoring.md and docs/implementation/ADDING_A_MODULE.md.
Edit the main checkout. No em dashes, no generated filler and no learner-state writes.

track.json defines the learning route; lessons.json registers only complete authored sets.
Each lesson needs a standalone guide with prerequisites, vocabulary, syntax anatomy,
at least two distinct worked examples with expected output, misconceptions, six inspectable
exercises, progressive hints and a lesson-specific Codex coaching prompt. Keep learner source,
executable reference and explained solutions separate. Explain every exercise's mechanism
and validate the answer against boundary/invalid inputs. Advanced lessons must explain
tradeoffs and failure diagnosis, not only introduce an API. Check official documentation.

Java sources run as Main.java with public class Main, no package declaration, Java 21,
and assertions enabled. Helper classes may share that file. Multi-file builds and external
libraries need explicit separate setup and cannot be assumed in the pad. Node uses main.mjs.
TypeScript uses main.mts, strict NodeNext checking then Node24 execution. Only prepared
built-ins and Node typings are available. Do not run npm install from an example.
Browser DOM APIs do not exist in Node. DOM lessons currently use reading mode with separate
browser files/instructions; do not register fake Node execution for document/window examples.
Runtime operations and profiles are controlled by backend code, never by manifests.

Use deterministic offline examples and honest expected results. Run references in the
corresponding prepared Docker worker before calling the lesson execution-verified.
Preserve stable IDs and prerequisites; coordinate changes to shared loaders with root.

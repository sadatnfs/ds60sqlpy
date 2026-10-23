# Java authoring checkpoint

Updated2026-10-22. User priority shifted to detailed applied LLM/NLP teaching, so Java authoring is paused after a coherent first batch.

Completed authored IDs: `java-001` through `java-012`,12 of36 planned lessons. Each has a standalone guide, two complete worked Main.java examples, six concrete exercise contracts, an answer-free learner source, executable reference and separate explanatory solutions. `lessons.json` registers only these12. `java-013` through `java-036` remain unregistered and unfinished.

Portable original authoring sources are in `courses/java/authoring/`. Run `python courses/java/authoring/build.py` from the repository root to regenerate the authored batch. The renderer writes source text as UTF-8 and preserves explicit Java Unicode surrogate escapes.

No Java lesson reference has been compiled or executed by this authoring pass. Root owns prepared-image compilation and runtime receipts. Do not infer reference acceptance from the already qualified Java21 worker. Focused Java content tests remain to be added when this workstream resumes.

JDBC29 will use actual standard java.sql calls against an isolated H2 in-memory database. Root has selected the prepared driver path `/opt/course-libs/h2-2.5.252.jar`. No fake database should be labelled JDBC execution. No runtime package download belongs inside the lesson.

## Prepared-runtime acceptance readback

Root integration compiled and executed all12 authored Java references successfully in the prepared Java21/H2 Linux arm64 Docker image. Receipt: `work/java-lessons-acceptance.jsonl`. This supersedes the earlier authoring-pass unexecuted state for Java001..012. It does not claim the remaining24 Java lessons exist or that any native Windows/macOS Java environment was tested.

## Second coherent authoring batch and priority change

Java013..020 are now authored and registered,bringing the inventory to20 of36. The new batch covers functional interfaces,streams,time zones andDST,owned filesystem work,Optional contracts,tests that detect mutants,data structures and complexity,and binary search/stable sorting/dynamic programming. All have separate learner,reference and explanatory artifacts. The user then prioritized a dedicated PyTorch36 course matching TensorFlow depth,so Java021..036 remain unfinished and unregistered.

`tests/test_java_lessons.py` checks authored identity,paths,teaching depth,exercise separation and prerequisites. Its actual JDK execution cases are opt-in throughDS60_TEST_JAVA=1,with assertions enabled and bounded compiler/process time. Root owns prepared-container reference receipts for the new batch. The earlier12-reference Docker pass does not automatically validate Java013..020. Portable authoring sources now include all20 completed lessons.

## Third coherent authoring batch

Java021..028 are now authored and registered,bringing the inventory to28 of36. They cover thread happens-before relationships,controlled lost updates,executor timeouts/cancellation/backpressure,locks andatomics,Java21 virtual threads,heap reachability,actual two-module compilation/execution,JAR reproducibility and a short-lived loopbackHTTP fixture. These new references await root's prepared-image execution. Root confirmed Java013..020 all passed,so the first20 are now execution-verified in that Linux arm64 image.

The user then prioritized six expert transformer-mechanism additions to LLM theory. Java029..036 remain unfinished and unregistered until that coherent addition is completed. The module/build lessons still need their separately checked-in manual fixture layouts and commands before the final Java freeze. Portable authoring sources contain the full28-lesson batch.

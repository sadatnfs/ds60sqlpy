# JavaScript and TypeScript

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **JavaScript and TypeScript** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


All **42 lessons** are authored, with standalone guides, two worked examples, six practice tasks, answer-free learner files and separate explained solutions. The route connects language fundamentals, Node programs, strict TypeScript, browser interaction and application engineering. [The local manifest](lessons.json) registers complete bundles; [the route plan](track.json) preserves their stable IDs and prerequisites.

Start with [JavaScript, Node and the browser](guides/js-001.md). Predict the worked result, implement the tasks in a saved learner copy, then compare with the separate solution after an attempt.

- 001-009: values, coercion, loops, closures, arrays, objects, Map/Set, Unicode and validation.
- 010-018: real modules, generators, Promise scheduling, cancellation, algorithms, testing, files, HTTP and a bounded CLI.
- 019-028: strict TypeScript, unions, readonly aliasing, generics, type operators, runtime schemas, actual NodeNext projects, classes, async results and typed algorithms.
- 029-031: actual browser starter/reference files for events and focus, forms and scoped storage, safe DOM/URL construction and CSP.
- 032-037: streams and backpressure, workers and transfer, measurement, dates and timezones, package interfaces and retry/concurrency policies.
- 038-042: typed API contracts, state machines, a real local HTTP service, incremental analytics and verified release bundles.

## Execution contracts

The route contains 26 JavaScript references, 13 TypeScript references and three browser reading lessons. JavaScript uses prepared Node 24.22.1. TypeScript uses 5.9.3 with strict NodeNext checking and noEmitOnError, then runs emitted JavaScript on Node. Type annotations are erased and do not replace runtime validation.

Browser chapters use separate real HTML files. Their READMEs make Docker-only static serving the main route: a prepared image, new learner-owned copy, read-only mount and a dedicated loopback origin outside the authenticated classroom. Node does not execute their DOM interactions. No default lesson installs packages, calls a paid API or downloads assets.

Save learner work in a classroom pad or ignored `.learning/expansion/<lesson-id>/`. References own only their temporary directories and tiny local services. See [the implementation checkpoint](../../docs/implementation/javascript-content-status.md) for exact prepared-container and browser evidence. Authored content, passing fixture execution and learner mastery are distinct observations.

## Reproducible authoring

[Portable specifications](authoring/README.md) reproduce all source bundles. Root coordinates shared catalog, runtime and browser integration. Keep lesson IDs, direct prerequisites, code/error contracts and manual browser boundaries aligned when changing a chapter.

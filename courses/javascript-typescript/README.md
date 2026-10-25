# JavaScript and TypeScript

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **JavaScript and TypeScript** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


All **66 lessons** are authored, with standalone guides, two worked examples, six practice tasks, answer-free learner files and separate explained solutions. The route connects language fundamentals, Node programs, strict TypeScript, browser interaction and application engineering. [The local manifest](lessons.json) registers complete bundles; [the route plan](track.json) preserves their stable IDs and prerequisites.

Start with [JavaScript, Node and the browser](guides/js-001.md). Predict the worked result, implement the tasks in a saved learner copy, then compare with the separate solution after an attempt.

- 001-009: values, coercion, loops, closures, arrays, objects, Map/Set, Unicode and validation.
- 010-018: real modules, generators, Promise scheduling, cancellation, algorithms, testing, files, HTTP and a bounded CLI.
- 019-028: strict TypeScript, unions, readonly aliasing, generics, type operators, runtime schemas, actual NodeNext projects, classes, async results and typed algorithms.
- 029-031: actual browser starter/reference files for events and focus, forms and scoped storage, safe DOM/URL construction and CSP.
- 032-037: streams and backpressure, workers and transfer, measurement, dates and time zones, package interfaces and retry/concurrency policies.
- 038-042: typed API contracts, state machines, a real local HTTP service, incremental analytics and verified release bundles.
- 043-054: D3/SVG foundations, selections, keyed joins, scales, axes, data cleaning, time series, scatterplots, histograms, statistical summaries, composition and responsive components.
- 055-066: transitions and reduced motion, accessible interaction, brushing, zoom, trees, treemaps, force layouts, geographic data, choropleths, Canvas, coordinated dashboards and a complete analytical capstone.

## Execution contracts

The route contains 26 Node JavaScript references, 13 TypeScript references, three original browser reading lessons and 24 D3 browser-preview lessons. JavaScript uses prepared Node 24.22.1. TypeScript uses 5.9.3 with strict NodeNext checking and noEmitOnError, then runs emitted JavaScript on Node. Type annotations are erased and do not replace runtime validation.

The original js-029 through js-031 browser chapters use separate real HTML files. Their READMEs make Docker-only static serving the main route: a prepared image, new learner-owned copy, read-only mount and a dedicated loopback origin outside the authenticated classroom. Node does not execute their DOM interactions. No default lesson installs packages, calls a paid API or downloads assets.

The D3 specialization starts at [js-043](guides/js-043.md) and runs directly in
the classroom preview using the bundled D3 7.9.0 global, `#chart` and `#output`.
All inputs are inline and synthetic, with no CDN or dataset request. Saved
results are source-bound client observations and are never labeled as trusted
backend verification. [The D3 inventory](fixtures/d3-inventory.json) lists every
reference and completion marker for real-browser qualification.

Save learner work in a classroom pad or ignored `.learning/expansion/<lesson-id>/`. References own only their temporary directories and tiny local services. Use [validation](../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect prepared-container and browser results. Authored content, passing fixture execution and learner mastery are distinct observations.

## Browser design and live preview

For D3 lessons, enable **Live preview** to refresh the preview after you stop
typing briefly. Use desktop, tablet or mobile widths, inspect console errors
and pause or stop automatic updates when needed. Live refreshes do not create
run history; manual Run and explicit saved observations preserve the source
associated with their result. Switching lessons cancels the current preview.

The [HTML, CSS and PHP course](../web-development/README.md) develops semantic
markup, accessible forms, layout and server-side boundaries alongside this
language route. Its HTML/CSS lessons use the same classroom preview. Node's
worker and browser DOM execution remain distinct environments.

## Reproducible authoring

[Portable specifications](authoring/README.md) reproduce all source bundles. Root coordinates shared catalog, runtime and browser integration. Keep lesson IDs, direct prerequisites, code/error contracts and manual browser boundaries aligned when changing a chapter.

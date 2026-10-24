# JavaScript and TypeScript content checkpoint

Updated 2026-10-23. **All 42 stable IDs, js-001 through js-042, are authored and registered.** The route contains 26 JavaScript runtime lessons, 13 TypeScript runtime lessons and three browser reading lessons. Each has two self-contained worked examples, six inspectable tasks, expected observations, progressive hints, an answer-free learner artifact and separate explanations. Executable lessons also have a reference program.

## Concrete mechanisms

001-009 establish language/host distinctions, exact and approximate values, loop invariants, closures, ownership, prototypes, collection equality, Unicode and validation. Their initially compressed prose was repaired and manually read back.

010-018 use real temporary ESM/CommonJS modules, generator lifecycle events, controlled Promise traces, cooperative timer cancellation, binary search and heaps, actual passing/failing node --test children, UTF-8/CRLF chunk decoding, loopback HTTP and bounded NDJSON CLI processes.

019-028 explain static checking versus runtime validation, union exhaustiveness, readonly aliases, generics, conditional/mapped types, exact schema checks, real multi-file NodeNext compiler success/failure, private fields, typed async failure channels and BFS/dynamic programming. Compile-negative examples use narrow @ts-expect-error directives in uncalled functions. They are checked but not executed.

029-031 have separate starter and completed browser folders for native events, delegation, disclosure and listener teardown; forms and scoped localStorage with real cross-tab notifications; and textContent/parsed URL policy with external resources under restrictive CSP. Every folder has a local favicon. Docker-only serving uses --pull never, read-only learner-copy mounts and separate loopback origins. No screen-reader claim follows merely from ARIA attributes.

032-037 demonstrate actual backpressure/drain, pipeline abort and teardown, real workers and ArrayBuffer transfer, measurement without platform-specific speed claims, explicit timezone/locale behavior, actual package exports and private-path errors, and bounded retry/concurrency/idempotency policies. Controlled retry fixtures are labelled as such, not as real outage evidence. The idempotency store is explicitly in-memory.

038-042 add runtime-decoded typed API contracts, pure state-machine replay and retry budgets, an actual local HTTP service with safe metadata events, incremental UTF-8 analytics with rejected-row diagnostics and byte limits, and fresh-process release smoke checks with hash/path/runtime gates. Release examples do not publish or deploy anything.

## Execution evidence

All 18 foundation JavaScript references passed actual prepared Node24 offline Linux arm64 Docker execution: `work/javascript-first-018-acceptance.jsonl`.

All ten foundation TypeScript references 019-028 passed actual strict TypeScript5.9/Node24 Docker execution, including nested compiler projects in 025: `work/typescript-019-028-acceptance.jsonl`.

The final eight JavaScript references 032-037,040,042 and three TypeScript references 038,039,041 also passed actual prepared Docker execution. Receipts: `work/javascript-advanced-acceptance.jsonl` and `work/typescript-advanced-acceptance.jsonl`. Combined with the earlier batches, all 39 runnable reference programs have passing prepared-profile evidence. Development checks separately compiled and executed both worked programs per new lesson.

All three browser lessons passed actual Chromium interaction checks on separate Docker-served loopback origins. Receipt: `work/browser-fixtures-acceptance.json`. The checks include pointer/Enter/Space/Tab activation, nested and dynamic delegation, disclosure and focus, AbortSignal listener removal, malformed saved-data handling, actual two-tab notification, scoped reset, literal text rendering, same-origin URL decisions and an actual inline-script CSP block. Local app.js, style.css and favicon.svg loaded. No screen-reader qualification is claimed.

These checks cover the bounded fixtures and supported prepared environment. They do not establish production deployment, native platform parity or learner mastery.

## Tests and continuation

`tests/test_javascript_lessons.py` checks all authored paths, IDs, prerequisites, practice/explanation depth, every JavaScript reference and worked-example syntax, explicit opt-in Node/TypeScript execution, scoped storage, CSP/rendering boundaries and source/runtime error channels. Ruff and MyPy have been checked on the owned test file. Portable sources under `courses/javascript-typescript/authoring/` reproduce all 42 bundles and browser source fixtures.

The full route is frozen with its appropriate execution evidence. Address any later integration findings in both specifications and generated artifacts. Root owns shared runtime, Compose, navigation and delivery. No Git staging/commit/push, engine action, host-package installation or external model download was performed by this content workstream.

The requested TensorFlow/PyTorch/LLM quality pass remains required. Remove repetitive authored/beta/readiness boilerplate from learner guide openings while retaining relevant runtime limits. Expand topic-specific mechanisms, derivations, readable worked code, assumptions and diagnosis, especially the flagged llm-010 attention chapter. Keep qualification status in implementation documents rather than padding learner content. Word counts alone are not instructional-depth evidence.

# JavaScript and TypeScript authoring

The original 42 lesson bundles and the 24-lesson D3 extension have portable specifications. `specs.py` contains 001-009, `intermediate.py` 010-018, `typed.py` 019-024, `typed_advanced.py` 025-028, `browser.py` 029-031, `advanced.py` 032-037 and `applications.py` 038-042. `render.py` keeps guides, answer-free learner sources, executable references and explanatory solutions aligned. `browser_fixtures.py` creates only the checked-in starter and separate completed browser trees, never learner copies.

Run `python courses/javascript-typescript/authoring/build.py` from the repository root. It preserves stable plan IDs and runtime contracts. Raw Python strings preserve JavaScript/TypeScript backslash escapes; code containing nested child programs needs particular care. Parse references and worked programs, compile TypeScript with the pinned strict NodeNext flags, then execute in the prepared runtime. Browser behavior requires a real browser session.

The fixture READMEs use the prepared Docker image with --pull never, read-only mounts of new learner copies and separate loopback origins. No authoring script installs packages, downloads models or changes a runtime image. Maintained runtime constraints are in [the implementation checkpoint](../../../docs/implementation/CHECKPOINT.md).
Actual runtime results belong to immutable source-bound receipts and current
CI/check artifacts, not a historical status page.

## Unified classroom presentation

Author mathematical expressions with explicit LaTeX `\( ... \)` and standalone
`\[ ... \]` delimiters. Tag every fenced code example with its actual language.
After regenerating older prose sources, run `python scripts/normalize_lesson_prose.py --write`
from the repository root before rebuilding HTML readers. The reviewed
`curriculum/math-prose.json` registry preserves this migration across regeneration;
it does not change executable fences, notebook code or the supplied statistics
outline. The public learner entrypoint is `/classroom`, shared by every subject.
See [the content contract](../../../docs/content-authoring.md) for the rendering
and subject-theme requirements.

## D3 specialization

`d3_specs.py` and `d3_extension.py` own js-043 through js-066. The extension runs at the end of `build.py`, preserving the original 42 IDs. Each new reference is a complete `.js` program for `javascript-browser`, using bundled D3 7.9.0, `#chart` and `#output`, inline synthetic data and a stable completion marker. It never imports or fetches a library. A thrown error is a failed check; browser observation is not a trusted backend verifier.

`fixtures/d3-inventory.json` lists every starter, reference and marker for actual browser qualification. Use a fresh preview for each case and perform separate keyboard, narrow-screen and reduced-motion review. Code parsing or Node execution cannot qualify DOM behavior.

D3 references must stay error-free after interaction and viewport changes.
Inspect the current preview status and console as well as the initial marker;
a handled sandbox interaction error is still a failed observation. Schedule
ResizeObserver-triggered DOM writes on a guarded animation frame, and cancel
owned observers/animation work when the page leaves. The real classroom checker
covers this boundary, then a separate read-only phase checks original records
and final pads after actual container replacement.

Each lesson's worked example 2 is published as a complete preview program:
`d3_extension.worked_program` wraps the example body in the same setup as the
reference (`host`, `output`, `check` and an accessible `svg` in `#chart`), and the
body must draw marks and check its claim with `check`. Worked example 1 stays a
short snippet but must declare everything it uses. Per-task hints are the first
sentence of each task's explanation, and reference links are labeled by
documentation set and page.

## Outcomes and derived practice

`outcomes.py` holds one specific outcome for every ID from js-001 to js-066 and
optional `MINUTES` overrides (the D3 capstone). Both renderers refuse a missing or
templated outcome. The published `lab` and `verification` fields both come from
exercise or task 3.

For js-001 to js-042, Exercises 1 and 2 are derived from Examples A and B instead
of repeating them, and every `Verify` line and progressive hint names that
exercise's own check. Where recorded, they also name a one-token edit that was
executed and observed to make that check fail. The observations live in
`variants.json` and are refreshed after any exercise change:

```sh
python courses/javascript-typescript/authoring/qualify_variants.py
```

It needs a local Docker engine and the prepared `ds60sqlpy-worker-javascript-node`
and `ds60sqlpy-worker-typescript-node` images. Programs run offline with the
classroom's Node flags, and TypeScript is compiled first with the classroom's
strict NodeNext `tsc` flags. Unmodified references must pass first; a mutant counts
only when an assertion of the targeted exercise fails, not on a compile error,
timeout or other exception. The three browser reading lessons (js-029 to js-031)
have no Node runtime, so their practice is phrased as browser observations.
Rendering never executes code and stops with a clear message if an exercise
changed after its record was made.

## Shared routine and lesson guidance

The routine every lesson shares lives once in
[the study guide](../STUDY-GUIDE.md): running Node, TypeScript and browser
lessons, saved copies and the success receipt, predicting, using hints,
diagnosing a failure, sources, the D3 browser preview and completion marker,
D3 debugging checkpoints, accessibility review, statistical meaning and
retrieval practice. Guides link to its anchors instead of repeating it, so
rename an anchor only together with both renderers.

`guidance.py` supplies the paragraphs that differ between lessons. `GUIDANCE`
gives js-001 to js-042 a prediction trap, a characteristic pitfall, a retrieval
question and a fresh transfer case; `D3_GUIDANCE` gives js-043 to js-066 a
debugging path, an accessibility note, the statistical meaning, a retrieval
task and a transfer case shown after comparison. Every numeric claim in these
entries must match the lesson's own examples or a checked library behavior. Do
not add generic text that could apply to any lesson; put it in the study guide.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.

## Canonical Markdown publication

Use the [prepared contributor formatting toolchain](../../../docker/formatting/README.md),
including Prettier 3.6.2 and its locked JavaScript/TypeScript parsing dependencies,
when running the existing build command. Both the original renderer and the D3
extension pass completed guide/explanation Markdown through the shared
`canonical_markdown` guard before their normal writes. The adapter checks
generated-path ownership, syntax, protected literals and idempotence, while
reporting unsupported or opaque regions. Missing prepared tools fail explicitly;
there is no automatic installation or raw-output fallback.

The original specification order, D3 admission, standalone program assembly and
browser fixture generator are unchanged. This hook does not execute Node,
TypeScript or browser examples. Browser fixtures remain under their own source
contract and were not added to the Markdown hook.

There is no separate `--check` mode for this builder. Hash the output artifacts,
rerun in the same prepared environment and compare hashes. Continue through the
normal standalone source formatting and publication checks. Within the prepared
formatting environment, check admitted web-language fences with:

```sh
python scripts/format_inline_code.py --check --language web
```

Keep actual strict TypeScript compilation and browser/D3 interaction evidence
separate from source formatting. Existing publication assertions and historical
observations remain unchanged; generated HTML is still owned by shared readers.

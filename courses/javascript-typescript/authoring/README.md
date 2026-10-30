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

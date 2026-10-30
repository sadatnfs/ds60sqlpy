# Expert transformer authoring sources

These original specifications and renderer own `llm-043` through `llm-048`. Run `python courses/llm-theory/authoring/build.py` from the repository root. The plan update appends missing expert IDs only and preserves earlier IDs, prerequisites and pilot metadata. The renderer writes only the six authored expert bundles plus the shared LLM authored manifest and reviewed plan metadata.

Earlier llm-002 through llm-042 source ownership remains with the established original files and `courses/deep-learning-tensorflow/authoring/` specifications. Regenerating that earlier authoring set preserves the six expert entries and files. Do not replace one authoring source with the other.

Every expert topic contains three worked demonstrations, six exercises, an explicit derivation and shape trace, a controlled case study, design tradeoffs and separate executable/explanatory solutions. Primary papers are linked in each guide. Default code uses only prepared NumPy or PyTorch CPU dependencies and does not download models or data.

## Detailed review and program preservation

`depth_reviews_foundations_expert.py` contains the reviewed mechanism and
counterexample additions for directly maintained `llm-001` through `llm-009`
and generated experts `llm-043` through `llm-048`. The expert renderer applies
this guide hook on every regeneration. `review_guides.py` reapplies only those
15 guide additions and prose spacing repairs in their explanatory solutions;
it does not write shared metadata, learner programs or executable references.
Every fenced program is excluded from prose transformations. The direct pilot
guides remain authoritative for their preexisting content.

The review's only approved executable changes were the llm-043/llm-046 attention helper
guards for zero head width and overflowed computed scores. Those changes live
in `specs.py`, the guide helpers and the executable references, with dedicated
regressions and fresh Docker receipts. The other 13 reviewed program/reference
sets remain byte-identical to the pre-review snapshot. Preserve those immutable JSON evidence files and source-format parity records.
[The current checkpoint](../../../docs/implementation/CHECKPOINT.md) records
durable limits; changed behavior requires new execution evidence.

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

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.

## Canonical displayed code

The owner renderer passes Markdown through the shared guarded fence formatter
before writing it. Python fences use the pinned Ruff tool already present in
the Core quality environment, with independent AST, literal and comment guards.
Missing tools fail explicitly; generation never installs a dependency or runs
framework examples. Formatting configuration comes from the renderer's stable
source root even when a regeneration test uses a temporary output directory.

For a formatting-only publication pass, run this directory's normal `build.py`
with `--markdown-only`. That mode writes guides and explanatory solutions while
preserving standalone learner/reference programs, plans, manifests and review
ledgers. Normal full generation retains its existing scope. After generation,
apply the maintained prose normalizer and the shared reader/TeX pipeline.

Historical execution and frozen-artifact receipts remain unchanged. Changed
Python fence layout needs the separate self-verifying
`curriculum/inline-format-parity.json` binding from a retained pre-format source
snapshot. Its verifier preserves non-code spans, fence identities, Python AST
values/type comments and ordered comments before exposing historical bytes for
old hash assertions. This is static formatting parity, not new execution.

The standalone textbook/review prose tools keep their code-preserving default.
Their explicit `--canonical-code` mode also canonicalizes displayed Python;
normal owner builds request it after the prose layer. Use
`python courses/llm-theory/authoring/review_guides.py --canonical-code` for the
reviewed pilot/expert guide and explanation surfaces that tool owns.

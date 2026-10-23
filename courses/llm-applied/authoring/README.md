# Applied LLM authoring sources

The topic specifications, literal decoder source, reviewed route and renderer maintain all24 lesson bundles. Run `python courses/llm-applied/authoring/build.py` from the repository root after editing. The renderer preserves code blocks while polishing prose punctuation, includes shared helper code once in the worked sequence, and writes guides, learner worksheets, separate solutions and manifests. Later worked blocks deliberately reuse earlier fixture state, as the guides explain.

Optional pretrained files under `fixtures/pretrained/` and the course README are maintained directly and are not downloaded or executed by this renderer. The optional guide link is stored in its topic specification. The renderer does not alter runtime adapters, shared generators, learner state or package environments.

## Substantive review and frozen programs

`depth_reviews_applied.py` adds stage-specific derivations, interview reasoning and diagnosis through the final hook in `specs.py`. It preserves the independently owned LoRA016 module and optional pretrained fixture. `review_matrix.json` records all24 completed reviews. `review_baseline.json` preserves pre-review reference and sequential-program identities; `review_runtime_evidence.json` binds the three repaired references and two changed worked sequences to observed worker receipts.

The only executable repairs in this review are010 integer hop-budget admission,015 post-update training-loss reporting and022 stable finite grouped means. All other references and worked sequences remain byte-identical to their saved baseline. Run `python -m pytest tests/test_llm_applied.py -q` with the prepared development interpreter to check that preservation, review completeness and current receipt hashes. Runtime proof remains separate from host skips. The three worked Python blocks execute sequentially; reading021 uses written cases and its own explicitly optional pretrained workflow.

## Connected textbook edition

`textbook_applied.py` contains the24 connected chapter narratives and learner-facing overviews. It follows the Methods Desk analytical-assistant case from task choice through evidence, domain training, tools and evaluation. The renderer places those narratives in the guides while preserving the existing worked programs and optional recipe.

For prose work, regenerate only the guides:

```text
python courses/llm-applied/authoring/build.py --guides-only
```

This mode skips the plan writer, manifest writes, learner/reference writes and review-matrix writes. The ordinary build also includes the textbook narratives, but should be used only when intentionally regenerating the whole course. `textbook_protected_artifacts.json` records73 frozen files, including both course manifests, and97 pre-existing fences. The focused test checks every byte/hash. Earlier runtime receipts retain their historical full-guide hashes; their executed-program hashes remain exact after this prose edition. `textbook_parity_receipt.json` records the final verification.

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

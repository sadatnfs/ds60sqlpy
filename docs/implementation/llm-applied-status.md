# Applied LLM content, depth review and execution checkpoint

Updated 23 October 2026. All **24 lesson bundles are authored and substantively reviewed**. This pass reviewed23 chapters; the independently completed LoRA016 review was preserved. Lesson021 remains a reading chapter with a separate optional pretrained recipe. The other23 use their existing17 Core and six PyTorch runtime profiles. No default program downloads a model or dataset.

## Completed topic review

The review adds explicit formulas, state/shape traces, counterexamples, stage-specific decisions, diagnosis and69 explanatory interview answers across the23 reviewed chapters. It distinguishes literal retrieval/extraction baselines, actual tiny-model training, observed pretrained mechanics and domain-quality acceptance. The [machine-readable matrix](../../courses/llm-applied/authoring/review_matrix.json) records every chapter's concrete findings and executable-change scope.

| Chapter | Substantive review outcome |
| --- | --- |
| [llm-applied-001](../../courses/llm-applied/guides/llm-applied-001.md) | Stage-level routing, capability evidence and conditional pipeline success |
| [llm-applied-002](../../courses/llm-applied/guides/llm-applied-002.md) | Typed extraction, provenance coordinates, estimands and rejected-record coverage |
| [llm-applied-003](../../courses/llm-applied/guides/llm-applied-003.md) | Context overhead, greedy allocation, prompt identity and injection-test scope |
| [llm-applied-004](../../courses/llm-applied/guides/llm-applied-004.md) | Version lineage, historical applicability, integrity and source admission |
| [llm-applied-005](../../courses/llm-applied/guides/llm-applied-005.md) | Window-count derivation, overlap cost and Unicode citation coordinates |
| [llm-applied-006](../../courses/llm-applied/guides/llm-applied-006.md) | Exact BM25 scores, saturation, length normalization and corpus dependence |
| [llm-applied-007](../../courses/llm-applied/guides/llm-applied-007.md) | Cosine geometry, encoder-space compatibility and search-versus-relevance recall |
| [llm-applied-008](../../courses/llm-applied/guides/llm-applied-008.md) | Exact RRF gaps, correlated rankings and reranking evidence ceilings |
| [llm-applied-009](../../courses/llm-applied/guides/llm-applied-009.md) | Pre-filtering, cache equivalence, revocation and trusted policy inputs |
| [llm-applied-010](../../courses/llm-applied/guides/llm-applied-010.md) | BFS frontier, integer hop bounds, branching and semantic bridge limits |
| [llm-applied-011](../../courses/llm-applied/guides/llm-applied-011.md) | Span integrity, entailment, computed claims and abstention utility |
| [llm-applied-012](../../courses/llm-applied/guides/llm-applied-012.md) | Cutoffs, macro/micro denominators, oracle controls and saved-label scope |
| [llm-applied-013](../../courses/llm-applied/guides/llm-applied-013.md) | Exact family-bootstrap distribution, pairing and selective-answer metrics |
| [llm-applied-014](../../courses/llm-applied/guides/llm-applied-014.md) | Shifted answer masks, conditioning gradients, truncation and packing boundaries |
| [llm-applied-015](../../courses/llm-applied/guides/llm-applied-015.md) | Decoder shapes/parameter counts, target gradients and final-state loss reporting |
| [llm-applied-016](../../courses/llm-applied/guides/llm-applied-016.md) | Independent LoRA orientation, first-step derivatives, rank and merge review |
| [llm-applied-017](../../courses/llm-applied/guides/llm-applied-017.md) | Quantization codes/bytes, output error, adapter objective and memory levels |
| [llm-applied-018](../../courses/llm-applied/guides/llm-applied-018.md) | Controlled SFT/adapter state, target modules and optimization-budget limits |
| [llm-applied-019](../../courses/llm-applied/guides/llm-applied-019.md) | Preference derivative/curvature, reference identity and scalar-versus-policy scope |
| [llm-applied-020](../../courses/llm-applied/guides/llm-applied-020.md) | Retrieval projection/reranker gradients, analytic boundary and negative-label quality |
| [llm-applied-021](../../courses/llm-applied/guides/llm-applied-021.md) | Qualified pretrained evidence ladder, real masks, repeatability and quality failure |
| [llm-applied-022](../../courses/llm-applied/guides/llm-applied-022.md) | Typed analysis grain, stable finite means, reporting lineage and causal limits |
| [llm-applied-023](../../courses/llm-applied/guides/llm-applied-023.md) | Time boundaries, admitted attempts, cancellation and trace-value contracts |
| [llm-applied-024](../../courses/llm-applied/guides/llm-applied-024.md) | Actual integrated call path, coverage, evidence gates and bounded no-go |

The guides contain about2136-3283 whitespace words each after this pass. Counts describe size; the derivations, independent counterexamples and explicit limits are the content evidence. Every guide retains three worked cases, six distinct tasks and separate learner/reference/explained artifacts. Reading021 now has a written-case study contract instead of instructions to execute its text cases as a program.

## Durable authoring and code preservation

The separate `authoring/depth_reviews_applied.py` supplies the new explanations through a hook after the existing LoRA review. It adds to the rendered anatomy and decisions and replaces generic diagnosis. The original `lora_depth.py`, its derivative oracle and the optional pretrained fixture remain separately owned and were not changed by this review. The applied renderer now gives Docker-first directions while preserving the declared profiles.

An immutable [review baseline](../../courses/llm-applied/authoring/review_baseline.json) records reference and sequential worked-program hashes before the pass. Tests require every unchanged program to match that baseline. The only reference behavior changes are010,015 and022; only010 and022 change the sequential worked program. All other default executable content is byte-identical to the baseline. The three A-C blocks remain one documented sequential fresh-process program.

## Concrete repaired defects and runtime evidence

- **010, bounded graph traversal:** fractional max_hops previously passed validation but could never equal an integer depth, so it bypassed the intended stop. The helper now requires a nonnegative Python integer and rejects fractional, Boolean, NaN and negative budgets before traversal. Reference and sequential guide both passed current Core Docker. Receipts: `work/applied010-depth-repaired-acceptance.jsonl` and `work/ml-worked-applied010-depth-repaired-acceptance.jsonl`.
- **015, training receipt:** curve[-1] described the state before the twentieth optimizer update while held-out loss described the state after it. Final training loss is now recomputed from the same frozen final model and checked in the receipt. The changed reference passed current PyTorch CPU Docker in `work/applied015-final-state-repaired-acceptance.jsonl`. The worked A-C program was unchanged.
- **022, grouped mean:** finite values[1e308,1e308] could overflow an intermediate sum despite having a finite mean. Scaled summation now returns1e308 and handles opposite-sign cancellation, with an output-finiteness check. Reference and sequential guide passed current Core Docker. Receipts: `work/applied022-stable-mean-repaired-acceptance.jsonl` and `work/ml-worked-applied022-stable-mean-repaired-acceptance.jsonl`.

The checked-in [review runtime evidence](../../courses/llm-applied/authoring/review_runtime_evidence.json) preserves all three reference and two guide-program results with source/image identities and applicable worker/guide hashes. Focused tests recompute those hashes. Qualification used the existing bounded production worker, network disabled, read-only course mounts and one2CPU slot at a time. This author did not build images, acquire models or modify the optional fixture.

Earlier parent-owned receipts establish all23 default references and the sequential example baseline: `work/applied-llm-core-acceptance.jsonl`, `work/applied-llm-torch-acceptance.jsonl` and the records associated with `work/ml-sequential-examples-manifest.json`. The current three repairs are covered by the new receipts above rather than being attributed to older source versions.

## Focused validation

The applied suite now passes **36 tests**, with six explicit host-side PyTorch execution skips. The combined applied/PyTorch command passes **46 tests with44 declared host runtime skips**. Actual heavy-runtime proof is the separate prepared-worker evidence above; skipped host tests are not presented as numerical execution. Both test files pass Ruff, formatting and strict MyPy. The new prose-review module also passes strict MyPy. A read-only independent review verified the017 quantization/adapter derivatives and020 projection/reranker arithmetic, and clarified that gradients do not flow through discrete tokenization. Additional NumPy checks covered exact source spans,2805 chunk-window configurations, the RRF score gap, the family-bootstrap distribution, parameter counts and preference arithmetic.

The checks cover complete routes and profiles, practice/depth contracts, literal Core execution, chunk coordinates, independent BM25 arithmetic, vector failures, duplicate-resistant fusion, access-separated caches, integer-bounded cyclic traversal, answer masks, restricted-answer nondisclosure, optional asset tamper detection, local-only loading, the preserved LoRA finite-difference oracle, complete review records, immutable unchanged-code baselines and matching repair receipts.

## Optional pretrained execution and its observed quality failure

The separate recipe is fully documented under [fixtures/pretrained](../../courses/llm-applied/fixtures/pretrained/README.md). Parent-owned evidence records locked preparation, explicit pinned acquisition, offline local loading, mask inspection, ten full-SFT updates, ten LoRA updates and saved-adapter reload on Linux arm64. Full SFT updated134515008 parameters; LoRA updated230400. The supplied data has four authored training records and one held-out entity label sharing an extraction task/template. Its loss changes are mechanics observations, not an independent domain benchmark.

The saved adapter generated an incorrect conversion formula despite supplied correct evidence. That output was not accepted as a supported answer. The review retains this concrete failure: successful acquisition, training, saving and reload do not establish subject-assistant quality. Two same-environment LoRA runs matched artifact hashes and loss after seed placement was corrected before construction. Platform locks for other architectures are preparation evidence, not executed platform qualification.

The reading chapter separates this observed maintainer run from a hypothetical new learner who has not yet acquired assets or trained. A learner still needs an explicit optional preparation and execution path. The capstone's pretrained_generation_executed=False field concerns its local extractive run, not the separately executed recipe.

## Remaining evidence limits and handoff

There are no pending chapter-authoring or changed-program requalification gaps in this review. The explanations retain bounded local limits: metadata comparisons are not automatically integrated authorization gates; an extractive span constructor is not a general entailment checker; finite score fixtures are not a calibrated relevance model; low teacher-forced loss is not generation quality; local clocks/counters do not implement remote deadlines or real identity-provider integration.

The default capstone is an access-filtered fixed-lookup/extractive baseline with a separate validated calculation. It does not secretly integrate the learned retriever, tiny decoder, dynamic revocation service or pretrained adapter. Its local success and no-go production decision remain compatible. Root owns final evidence-index refresh, generated classroom/readers, full-suite checks and browser delivery. No further executable changes are pending from this author.

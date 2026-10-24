# ML explanation-depth review

Updated 2026-10-23. This is the current semantic-review ledger for TensorFlow 36, PyTorch 36, LLM theory 48 and applied LLM 24. It replaces historical partial counts. Complete authoring, successful reference execution, explanation review and production model quality are distinct claims.

## Current scope and ownership

| Route | Semantic review state | Detailed record |
| --- | --- | --- |
| TensorFlow 36 | All 36 reviewed: pilots001-008, prose additions009-017/019-030/032-036, rewritten018/031 | [TensorFlow review](tensorflow-depth-review.md) |
| PyTorch 36 | All 36 reviewed by the statistics author; behavior-changing cases separately requalified | [PyTorch status](pytorch-content-status.md) |
| LLM theory 48 | All 48 reviewed: middle chapters 010-042 plus foundations 001-009 and experts 043-048 | This ledger and [expert status](llm-expert-status.md) |
| Applied LLM 24 | All 24 reviewed; LoRA016 and the other 23 chapters have separate detailed records | [Applied status](llm-applied-status.md) |

All four parallel explanation reviews are complete. The routes have current executable-reference evidence, and the review ledgers identify the limited conclusions supported by the small teaching fixtures. This table records explanation review separately from execution or production model quality.

## Presentation and execution-contract repairs

Repetitive authored/beta/readiness banners were removed from guide openings and durable renderers. Specific offline, runtime and manual-fixture limits remain where they affect learner choices. Docker classroom directions are primary; native study is an optional linked route. Reading-only chapters now ask for written calculations and evidence tables instead of running text blocks.

The original TF/LLM completion renderer incorrectly let some Example B blocks depend on Example A while claiming independent fresh-process execution. Ordinary executable blocks now include required setup; custom examples can declare complete preambles. All 115 repaired programs passed separately in prepared Docker processes:35 Core,50 TensorFlow and30 Torch. Their inventory is `work/ml-worked-examples-manifest.json`, with source and guide hashes. The corresponding acceptance files are `work/ml-worked-{python-core,tensorflow-cpu,llm-torch-cpu}-acceptance.jsonl`.

The initial runnable pilots explicitly use sequential A+B programs, and expert chapters use sequential A-C programs. The cross-track sequential inventory `work/ml-sequential-examples-manifest.json` contains 43 complete programs; all passed Docker. Applied016 has its own sequential PyTorch chain and standalone NumPy gradient audit. The dedicated PyTorch author tracks that route's examples separately. An individual later sequential block is not advertised as standalone.

## Mechanism rewrites that changed executable code

| Chapter | Substantive correction | Evidence |
| --- | --- | --- |
| llm-010 | Derives query/key relabelling, positional order and LayerNorm statistics; readable NumPy helper; masked-prefix and upstream-leakage counterexamples | Reference plus three standalone examples; independent tests for rectangular permutations, mask relabelling and epsilon variance |
| llm-011 | Actual multi-head attention with distinct per-head mixtures, exact split/rejoin membership, residual cancellation and tokenwise FFN | Reference plus two standalone examples; head-group permutation and unmasked future-perturbation negative control |
| llm-016 | Full 10,464-parameter ledger, stage-by-stage shapes, pre-norm/residual equations, target shifting, cache bytes and readable decoder with explicit invalid-shape guards | Reference plus two standalone examples; actual Torch qualification |
| tf-018 | BatchNorm retained channels versus LayerNorm reduced features; rank-four axes; asymmetric Keras/PyTorch momentum; moving variance and trainable-state semantics | Reference plus three standalone examples; actual TensorFlow state checks |
| tf-031 | Tracing and graph execution versus explicitly requested XLA; warmed result checks and rank/dtype signature failures | Reference plus two standalone examples; actual TensorFlow execution |
| llm-applied-016 | LoRA factor and input gradients, scale-two first update, actual rank, merge/state boundaries and independent finite differences | Expanded reference, sequential A-C Torch examples and standalone NumPy oracle |

These revised references have successful current-source Docker receipts in `work/current-reference-evidence.json`. Narrow worked-program receipts include `work/ml-worked-heads-depth-acceptance.jsonl` and `work/ml-worked-tensorflow-depth-acceptance.jsonl`; decoder and LoRA inventories are `work/ml-decoder-depth-manifest.json` and `work/ml-depth-followup-manifest.json`. Older program hashes are superseded only where the executable actually changed.

One important negative-control repair used moderately scaled queries and keys: saturated self-attention had made two different masks look almost equal under a loose tolerance. The corrected fixture exposes the information-boundary error rather than widening the acceptance tolerance.

## Theory prose review: exact completed IDs

The following 33 chapters were inspected against their actual source and expanded with topic-specific calculations, assumptions and diagnosis. A prose addition does not turn an authored fixture or a saved answer record into a new model experiment.

| IDs | Reviewed mechanism and interpretation |
| --- | --- |
| 010-011 | Permutation relations, causal order, tokenwise normalization, head layouts, actual attention mixtures and residual/FFN behavior |
| 012 | Temperature probabilities, top-k support, inverse-CDF intervals and sampling versus correctness |
| 013-014 | Objective versus information boundary, complete smoothed count table, held-out likelihood and baseline scope |
| 015-016 | Gradient accumulation/detach, exact parameter and shape ledger, shifted prediction and cache state |
| 017 | Active-token denominator, logit gradients and padding-loss masking |
| 018-020 | Pre-update training curves, optimizer state, isolated one-batch overfit controls, initialization/loss/gradient scale and first-overflow diagnosis |
| 021-022 | Raw/normalized/family/assignment identities, Adam restart state, RNG and evaluation-mode scope |
| 023-024 | Top-p crossing token and vocabulary mapping, EOS/caps, cache position, ownership, invalidation and detached-gradient boundaries |
| 025-026 | Score versus cache byte formulas, peak-memory exclusions, probe decodability versus causal use and the actual control that ran |
| 027-028 | Calibration bin sensitivity, paired-ID errors hidden by means, exact baseline held-out loss and tiny-holdout limits |
| 029 | Unique corpus tokens versus processed tokens/steps, log-log slope and unidentifiable scaling floor |
| 030 | Raw/derived provenance, benchmark ancestry, selection contamination and permission versus independence |
| 031 | Shifted answer-mask alignment, uniform logits hiding a mean-loss error, gradients and prompt conditioning |
| 032 | Scale-one LoRA first update: gradient B0.25, output0.95, loss0.9025; frozen-parameter versus input-gradient semantics |
| 033 | Reference-relative preference margin, stable logistic loss, derivative and scalar-objective versus policy-training scope |
| 034 | Exact shared/per-row quantization output, unclipped half-step error bound, rounding/clipping and intended layout versus actual allocation |
| 035 | Per-request cache trace, version binding, serial interleaving versus batching, aggregate capacity and timing scope |
| 036 | Lexical score/relevance arithmetic, zero-overlap ranking, missing evidence and retrieval-text authority |
| 037 | Retrieval/answer/abstention decomposition, literal versus actually rerun oracle controls and citation entailment |
| 038 | Strict proposal schema, typed dispatch, operation/resource allowlists and actual read-only capability |
| 039 | Zero-failure finite bounds, independence assumptions, justified counterfactual invariance and severity gates |
| 040 | Row versus family weighting, exact two-family bootstrap support, coverage/conditional accuracy and selection boundaries |
| 041 | Rectangular projection orientation, API-specific mask shape/polarity, functional dropout and literal-weight parity |
| 042 | Authored candidate ledger versus executed random-decoder parity, hash scope, declared versus enforced budgets and three-state gates |

The exact mathematical values for the last batch were independently computed with NumPy and the standard library in `work/ml-theory-review-arithmetic.json`. In particular, theory032 uses scale one and therefore differs from applied016's scale-two result. The quantizer's shared output error is about0.012598425, the per-row error about0.001574803, and the unclipped bound about0.020078740. The finite zero-failure example is explicitly conditional on independent Bernoulli sampling, not a general guarantee for correlated prompt families.

## Prose parity and durable source

`courses/deep-learning-tensorflow/authoring/depth_reviews_llm.py` supplies30 prose additions;010,011 and016 retain their separate detailed modules. The original renderer can update guides alone. The source for TensorFlow's26 prose additions is `depth_reviews_tf.py`; pilots remain independently authored.

Exact unchanged Python-block and executable-reference hashes are recorded for the three theory batches:

- `work/ml-llm-prose-pass1-parity.json`:012-015 and017-020.
- `work/ml-llm-prose-batch2-parity.json`:021-028.
- `work/ml-llm-prose-batch3-parity.json` and its final-spacing readback:029-042.

The subsequent Docker-first refresh across35 owned guides also preserved every learner/solution artifact and every Python fence byte for byte in `work/ml-owned-docker-paragraph-parity.json`. Root's TensorFlow records independently preserve108 learner/solution files and52 worked blocks in its26-guide batch, plus14 pilot Python blocks.

Latest focused host validation reports110 passed and125 explicit framework skips. All78 current executable references in TensorFlow 36 plus theory 48 were separately rehashed against successful Docker receipts. No new runtime claim is inferred from prose length, an import, a parser result or a structural minimum. Detailed current counts and regeneration boundaries live in [ML content status](ml-content-status.md).

## Final foundations, experts and applied review

The final 15 theory guides, 001-009 and 043-048, were inspected and deepened.
Their combined guide text grew from 27,851 to 39,298 words through concrete
conditional-denominator, Unicode/BPE, gradient, cache, routing and normalization
explanations. Thirteen executable/worked sets are unchanged. Attention helpers
043/046 now reject empty head widths and nonfinite computed scores before
normalization. Two references, two sequential worked programs and two dedicated
extreme-input guards passed actual Core Docker, recorded in
`work/llm-attention-guard-docker-acceptance.jsonl`. Exact prose/code parity is in
`work/llm-foundations-expert-review-parity.json`.

All 24 applied chapters are reviewed. Three concrete repairs have fresh Docker
evidence: 010 rejects fractional/Boolean/nonfinite graph-hop budgets; 015 reports
training loss from the final model rather than the pre-update curve point; 022
uses scaled summation so a finite group mean does not overflow unnecessarily.
The changed 010/022 worked sequences also passed fresh processes. The optional
pretrained recipe retains its separate mechanics-success and answer-quality
failure evidence. See [the applied review matrix](llm-applied-status.md).

# TensorFlow and LLM theory: current content checkpoint

Updated 2026-10-23. This is the current source and execution checkpoint, replacing earlier authoring-stage waiting lists. It distinguishes a complete lesson bundle, a successful bounded runtime check and evidence about a model's practical quality.

## Current inventory

| Route | Complete IDs | Core / NumPy | TensorFlow CPU | PyTorch CPU | Reading |
| --- | --- | --- | --- | --- | --- |
| TensorFlow and Keras | `tf-001` through `tf-036` | 8 | 27 | 0 | 1 |
| LLM mechanisms and evidence | `llm-001` through `llm-048` | 27 | 0 | 16 | 5 |
| Combined | 84 chapters | 35 | 27 | 16 | 6 |

Every chapter has a guide, an answer-free learner artifact and separate explained solutions with six distinct practice cases. Every executable chapter also has an assertion-bearing reference program. Reading IDs are `tf-001`, `llm-001`, `llm-029`, `llm-030`, `llm-039` and `llm-041`; they require written reasoning, not a fabricated execution receipt. Stable IDs, prerequisites and profiles remain in the reviewed plans and authored manifests.

The [TensorFlow route](../../courses/deep-learning-tensorflow/README.md) and [48-chapter LLM route](../../courses/llm-theory/README.md) lead with the Docker classroom. [Inside a Transformer](../learning/inside-a-transformer.md) adds a connected numerical forward-pass companion. [Applied LLM systems](../../courses/llm-applied/README.md), [PyTorch](../../courses/deep-learning-pytorch/README.md) and [NLP](../../courses/nlp/README.md) have separate inventories and checkpoints; their counts are not folded into this table.

## Current executable evidence

All **78 executable references** in these two routes have successful prepared-container receipts matching their current source hashes. The local consolidated index is `work/current-reference-evidence.json`; this review independently checked every matching record and recomputed every reference SHA-256 from the current files. It records 35 Core, 27 TensorFlow and 16 PyTorch cases for these routes, within the larger product inventory. Earlier awaited-runtime statements are superseded.

Qualification used bounded offline CPU execution in the prepared Linux arm64 images. It does not establish Windows-native or amd64 execution, GPU performance, multi-device execution, production model quality or learner mastery. No default lesson downloads a dataset or model or calls an online model service.

Reference and worked-example execution are distinct checks. The guide program contracts are explicit:

- The initial runnable pilots use sequential A+B blocks in one fresh process. The six expert chapters use sequential A-C demonstrations. A later block may intentionally use the named state from the preceding one.
- The original completion chapters use independently runnable worked programs. The renderer includes needed setup in each ordinary block, and custom examples can supply their own complete preamble.
- The repaired 115 standalone worked programs passed actual fresh Docker processes: 35 Core, 50 TensorFlow and 30 PyTorch. Receipts are `work/ml-worked-python-core-acceptance.jsonl`, `work/ml-worked-tensorflow-cpu-acceptance.jsonl` and `work/ml-worked-llm-torch-cpu-acceptance.jsonl`.
- The separate 43-program sequential qualification batch covers original pilots, expert chapters and applied examples under their declared sequential contracts. Its inventory is `work/ml-sequential-examples-manifest.json`; this count is cross-track and is not 43 additional theory chapters.
- Subsequent mechanism rewrites have narrow replacement evidence: `llm-011` reference and two standalone examples passed in `work/ml-worked-heads-depth-acceptance.jsonl`; `llm-016` reference and two standalone examples passed the decoder qualification batch; `tf-018` and `tf-031` references and five worked programs passed in `work/ml-worked-tensorflow-depth-acceptance.jsonl`. These replace older worked hashes only for the changed programs.

The preserved subprocess checks distinguish restartable optimizer state from inference export. `tf-028`, `tf-032` and `llm-022` compile embedded child programs and report child stderr on failure. `tf-032` retains the loaded SavedModel owner while invoking its endpoint so captured variable resources remain alive. All repaired cases subsequently passed their actual framework runs.

## Semantic explanation review

All 36 TensorFlow chapters have received the topic-specific depth review recorded in [the TensorFlow ledger](tensorflow-depth-review.md). It includes the initial eight independently authored chapters, 26 prose additions and the two rewritten normalization/tracing chapters. The latter explicitly distinguish BatchNorm's retained channel axis from LayerNorm's reduced feature axis, asymmetric momentum conventions, and graph tracing from optional XLA compilation.

All 48 LLM theory chapters have completed substantive review: the ML author covered `llm-010` through `llm-042`, and the systems reviewer completed `llm-001` through `llm-009` and `llm-043` through `llm-048`. Current inspection and exact-code evidence are recorded in [the depth-review ledger](ml-depth-review.md) and [the expert checkpoint](llm-expert-status.md). The final attention guards in 043/046 and their changed worked programs passed a separate six-case Core Docker batch.

The reviewed middle chapters now derive concrete probability, gradient, state and evaluation quantities. Examples include the exact 10,464-parameter decoder ledger, actual multi-head mixtures, shifted-token gradient denominators, Adam restart scope, top-p crossing-token logic, score/cache byte formulas, probe decodability versus causal use, calibration bin effects, a count-baseline held-out loss, the first scale-one LoRA update, quantizer error bounds and family-weighted evaluation. The capstone explicitly labels its saved candidate decisions as authored records, separate from its actual random-decoder cache check.

The limitations are stated where they affect interpretation: serial scheduling is not a batched GPU measurement; dequantized NumPy multiplication is not an integer kernel; two scaling points do not validate a law; a citation substring is not entailment; zero failures in a tiny sample do not imply zero population risk; a hash does not bind an unrelated answer ledger to a model. [The review ledger](ml-depth-review.md) records exact chapter batches and unchanged-code receipts.

## Focused host validation

The latest full focused run of `tests/test_ml_module_lessons.py` reports **110 passed and 125 explicit optional-runtime skips**. It covers complete planned-ID/path agreement, practice/depth contracts, core reference execution, independent numerical counterexamples, source parsing and fresh-process Core worked programs. The skipped framework cases require deliberately prepared TensorFlow/PyTorch dependencies; the successful Docker evidence above supplies their separate runtime tier. No host framework install was performed to bypass those switches.

The new prose calculations were checked independently with NumPy and the standard library. `work/ml-theory-review-arithmetic.json` records the scaling slope, LoRA update, preference losses, quantizer outputs/bounds, zero-failure interval calculation and family-weighted comparisons. This arithmetic record is not a population experiment.

## Durable authoring and regeneration boundaries

The first eight TensorFlow and first nine LLM bundles remain independently authored. Edit their Markdown and associated source directly; the completion generator intentionally preserves them.

The next 61 bundles, `tf-009` through `tf-036` and `llm-010` through `llm-042`, are maintained under `courses/deep-learning-tensorflow/authoring/`. `tf.py` and `llm.py` register the specifications; dedicated modules retain the detailed rewrites; `depth_reviews_tf.py` and `depth_reviews_llm.py` supply topic-specific prose. From a prepared maintainer interpreter:

```text
python courses/deep-learning-tensorflow/authoring/build.py
```

For a prose-only update, use the renderer's `write_all(only=selected_ids, guides_only=True)` after importing the appropriate specifications. Compare all Python fenced blocks and learner/solution artifacts before and after. The latest Docker-first refresh preserved all those bytes across 35 owned guides, recorded in `work/ml-owned-docker-paragraph-parity.json`.

The six expert bundles, `llm-043` through `llm-048`, have separate sources under `courses/llm-theory/authoring/`:

```text
python courses/llm-theory/authoring/build.py
```

That workflow preserves the earlier 42 bundles and derives the README index from the plan and manifest. `authoring/readme.py` can refresh that index alone. Neither course authoring workflow changes worker implementations, runtime credentials, learner state, shared catalog registration or the practice baseline. Root integration owns catalog/navigation/reader generation and final browser delivery checks.

When executable code changes, create a narrow inventory with the current source hashes and obtain a new matching runtime receipt. A prose-only guide hash change does not invalidate unchanged program bytes. Keep current status here coherent rather than appending contradictory historical waiting lists.

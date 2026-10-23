# LLM textbook expansion: lessons 025-048

Updated 23 October 2026. All 24 assigned chapters are complete and ready for shared
reader/navigation generation. This pass changes connected exposition and chapter
bridges only. Every learner artifact, executable reference and fenced Python
example remains byte-identical to the snapshot taken before this textbook pass.
The previously approved043/046 numerical guards remain intact and unchanged.

## Durable source and regeneration

The readable chapter sources are
`courses/llm-theory/authoring/textbook_advanced/llm-025.md` through
`llm-048.md`. `textbook_advanced.py` inserts them into the existing purpose
section and replaces the generic next-step text with a chapter-specific bridge.
It leaves other IDs unchanged and verifies every fenced program and copy-ready
prompt. Each source has one explicit bridge delimiter and no executable fence.

The coordinated `apply_textbook.py` runner, owned by the foundations author,
invokes this layer after both existing authoring workflows. It supports selected
IDs and a strict completeness check. Neither shared renderer, plan, manifest,
README nor UI was edited in this pass. Isolated regeneration of 025-042 through
the original LLM specifications and 043-048 through the expert specifications,
followed by this hook, reproduced all 24 current guide files exactly.

## Concrete review notes

| Chapter | Added reasoning and independently inspectable distinctions |
| --- | --- |
|025 | Array lifetimes; materialized scores versus all-layer KV storage; batch padding; prefill/decode work; parameter/gradient/optimizer state. Worked 2048-token budget gives 128 MiB scores for one layer and 48 MiB cache across 12 layers under declared dtypes. |
|026 | Logistic-probe notation and first gradient[-.75,0]; decodability versus original-model causal use; fixed-predictor shuffle versus retrained controls; family splits; gradient, optimizer and buffer freezing. |
|027 | Event definition for confidence; bin boundaries; ECE.25 versus.05 under different bins; Brier.21; token/document weighting; paired IDs and selection leakage. |
|028 | Complete decoder shape path; exact 10,464 parameter count; pre-update curve timing; six training versus three holdout targets; independently derived smoothed baseline log(2754)/3; trained causality checks and hash limits. |
|029 | Distinct data versus processed tokens; optimization versus model scaling; fitted-floor counterexample; constrained size/token allocation derivation; training versus deployment objectives; invented-table limits. |
|030 | Raw/normalized/chunk/token lineage; admission versus transformation versus experiment role; duplicate-family graph; selection contamination; intended open-book source evidence versus hidden benchmark labels; version updates. |
|031 | Explicit shifted-target table; answer-only versus full loss gradients; ignored logit gradients versus prompt-representation influence; multi-turn formatting, truncation and active-target policy; SFT versus evidence acquisition. |
|032 | Adapter dimensions/rank; first-step gradient derivation; exact prediction.95 and objective.9025; zero-factor initialization; realized rank versus rank bound; optimizer membership; merged-artifact compatibility. |
|033 | Relative policy/reference margins; regularized-policy motivation; stable logistic loss and derivatives; improved margin despite lower chosen absolute probability; response-length and annotation effects; fixture versus full RLHF. |
|034 | Exact reconstruction and output errors; unclipped scalar/output bounds; per-row scale example; metadata byte costs; saturation; logit-margin sensitivity; representation versus integer-kernel performance. |
|035 | Five-action request/cache ledger; wrong-cache counterexample; prefill versus decode latency; logical positions versus physical batching; cancellation/eviction ownership; sampling state versus deterministic logits. |
|036 | Exact lexical score and tie behavior; nonempty zero-score retrieval; precision/recall denominators; context sufficiency and source versions; claim entailment; retrieved instructions as data; RAG versus adaptation. |
|037 | Four-case accuracy/coverage decomposition; sufficient context versus topical relevance; claim spans and semantic support; actual oracle-context intervention versus supplied fields; numerical computation versus narrative evidence. |
|038 | Parsing, schema, operation/resource allowlists, authorization and dispatch as separate stages; opaque IDs; inert retrieved commands; result validation; focused negative cases; read-only fixture limits. |
|039 | Zero-event binomial derivation with explicit assumptions; group denominators; justified counterfactuals; severe-failure gates; natural variation versus stress tests; unknown coverage versus zero risk. |
|040 | Paired loss estimand; row versus equal-family mean; exact two-family bootstrap probabilities; selection versus final assessment; abstention cost/coverage example; required evidence gates. |
|041 | Rectangular forward and backward weight translation; mask polarity and shape; boolean versus additive masks; cached coordinates; normalization/dtype/mode controls; explicit SDPA dropout; layered parity tests. |
|042 | Question/answerability contract; supplied candidate outcomes versus actual decoder probe; model/fixture hashes versus execution linkage; declared cap versus enforcement; unknown/failed gate handling; design of a real end-to-end study. |
|043 | Three attention paths; multi-layer causal dependency argument; objective versus architecture; masked conditional versus autoregressive joint scoring; label-shift leakage; source-streaming availability changes. |
|044 | Permutation-equivariance qualification; coordinate expansion of RoPE; frequency/layout identity; logical cache positions; ALiBi ratios versus hard access masks; numeric precision versus trained long-context behavior. |
|045 | LayerNorm/RMSNorm worked vector; centering-projection Jacobian; epsilon direction sensitivity; pre/post residual gradients; signed SiLU gating; branch derivatives; equal-budget FFN comparison. |
|046 | Head-sharing versus execution changes; projection/cache counts; exact two-block27/7 online-softmax trace; both accumulator rescalings; pair count versus storage; numerical-domain guards and hardware limits. |
|047 | Scores, assignments and gates; piecewise routing derivatives; top1 local-gradient consequence; capacity-factor arithmetic with unused capacity and overflow; balancing loss; stored versus activated parameters and dispatch identity. |
|048 | Full mass-preservation argument; total variation and support boundaries; conditional proposal prefixes; rollback length/position trace; EOS and caps; expected emitted-length/cost model; law versus same-seed text. |

The 24 guides grew from 48,838 to 75,082 whitespace-delimited words, ranging from
2,607 to 4,361 words each. Counts describe the artifacts, not the acceptance
criterion. The goal of the expansion is a connected explanation whose notation,
assumptions, worked reasoning and implications can be followed without a coach.
Existing practice contracts and separate solutions remain available.

## Validation and limits

- `work/llm-textbook-advanced-parity.json` records all 24 IDs, before/after guide
  counts, every unchanged Python-block count and learner/reference SHA256.
- All 24 guides passed strict completeness, idempotence, local-link and no-em-dash
  checks. Out-of-range ownership is preserved by the hook.
- Isolated ordinary authoring plus the textbook hook produced byte-identical
  current guides for both 025-042 and 043-048. No shared metadata was rewritten.
- Thirteen independent numeric checks passed for the new analytical traces,
  including memory counts, probe gradient, calibration, parameter count,
  baseline loss, quantization errors, LoRA update, zero-failure bound, framework
  gradient orientation, online-softmax merge and speculative-length sum.
- Focused ML/reference/guard checks reported 120 passed and 125 explicitly skipped
  optional TensorFlow/PyTorch host cases in 1.93s. Existing qualified Docker source
  receipts remain applicable because this pass changed no executable bytes.
- Ruff and strict MyPy passed for the isolated advanced prose hook. No new Docker
  run, package installation, model download or learner-state mutation occurred.

These chapters continue to distinguish exact arithmetic, supplied teaching
records, actual model execution, empirical task quality and operational proof.
The expanded prose does not turn toy models into pretrained systems or promote
an unexecuted workflow into runtime acceptance. Root owns final integration,
rendered pages, launchers, images and archives.

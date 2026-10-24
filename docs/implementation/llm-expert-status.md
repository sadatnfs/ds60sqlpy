# Expert transformer completion and review checkpoint

Updated 23 October 2026. The LLM route contains 48 authored lessons. All six
expert lessons, `llm-043` through `llm-048`, retain their stable IDs,
prerequisites, three sequential worked examples, six exercises and separate
executable/explanatory solutions. The 15-guide review described below covers
`llm-001` through `llm-009` and `llm-043` through `llm-048`; other agents own the
remaining LLM reviews.

## Expert mechanisms now explained

- `llm-043`: source/target availability, encoder and causal decoder flow,
  rectangular cross-attention, teacher-forced shifting, loss versus attention
  masks, backward axes and source-grounding limits.
- `llm-044`: coordinate-level rotary geometry, frequency/pairing layout,
  relative-offset identities, ALiBi weight ratios, cache offsets, position
  precision and the difference between computable indices and measured
  long-context quality.
- `llm-045`: RMSNorm radial/tangential Jacobian directions, epsilon and zero
  behavior, LayerNorm shift invariance, pre/post residual paths, actual PyTorch
  gradients, SwiGLU branch derivatives and equal parameter budgets.
- `llm-046`: grouped-head mapping, raw cache and projection counts, a changing-
  maximum online-softmax trace, both accumulator rescalings, exact arithmetic
  versus quadratic work, and hardware-performance limits. The NumPy routine
  is not a FlashAttention GPU kernel or benchmark.
- `llm-047`: selected-gate normalization, smooth local router derivatives versus
  discrete top-k boundaries, top1 router-gradient consequences, order-sensitive
  capacity admission, residual overflow, auxiliary-loss gradients and stored
  versus active expert resources.
- `llm-048`: accepted/residual mass, total-variation rejection probability,
  conditional-prefix stopping, bonus/EOS/budget rules, expected emitted length
  under explicitly simplified assumptions, and actual NumPy K/V rollback.
  Distribution preservation is separate from same-seed string identity.

The 15 reviewed guides increased from 27,851 to 39,298 whitespace-delimited words.
The nine foundations now range from 2,192 to 3,184 words; the six experts range
from 2,718 to 3,306. Counts describe the reviewed artifacts, not a quality gate.
Concrete findings and before/after program parity are recorded in
`work/llm-foundations-expert-review-parity.json` and the durable review data
module. New mathematical traces were independently checked, including the
router auxiliary gradient, speculative-length calculation and online-softmax
rescaling example. Local links, no-em-dash checks and repeated guide-review
idempotence passed.

## Two concrete helper repairs

Inspection found that finite Q/K elements can overflow while forming attention
scores. `llm-043` now controls numerical warning behavior during that operation
and raises ValueError for nonfinite allowed scores. `llm-046` now requires a
positive head width and uses a checked score helper in dense and online paths.
Undefined products and zero-width divisions no longer become accepted NaN
outputs. The fixes are aligned in `authoring/specs.py`, guide helpers and
executable references.

`tests/test_llm_foundations_expert_review.py` adds 10 independent cases covering
both reference and sequential worked helpers, finite extreme inputs, zero head
width, absence of emitted arithmetic warnings, and a nonuniform finite oracle.
These tests passed. The other 13 reviewed chapters retain their original
executable and worked Python bytes. No learner program was changed.

## Current validation

The focused host run of `tests/test_ml_module_lessons.py` plus the new guard
suite reported **120 passed, 125 skipped** in 2.41s. Skips explicitly require the
optional TensorFlow/PyTorch host runtimes; they are not reported as host passes.
Ruff and strict MyPy passed for the new test. The review data/guide helper also
passed Ruff. Isolated expert generation reproduced all six executable reference
files exactly, and the generated Python worked blocks match their current
guides. Shared plan/manifest files were not rewritten by this review.

All six expert references have actual offline, resource-bounded Linux arm64
Docker receipts. The initial receipts are
`work/llm-expert-core-acceptance.jsonl` and
`work/llm-expert-torch-acceptance.jsonl`. Sequential A-C execution is recorded in
`work/ml-worked-sequential-core-acceptance.jsonl` and
`work/ml-worked-sequential-torch-acceptance.jsonl`. The 045 proof executes real
PyTorch gradient examples, not a NumPy replacement.

For the two repaired helpers, the current superseding receipt is
`work/llm-attention-guard-docker-acceptance.jsonl`: both exact references, both
sequential A-C programs and both dedicated invalid-input programs passed,
**6/6**, through the production isolated-UID worker operation in the prepared
Core image. Its identity is
`sha256:ee87f7a78cf13a2398ef080c2790428500e43acb65a3b20780aeaa2fe780a0b2`.
Current reference and worked-source hashes match that receipt. The short-lived
proof container was removed; no image build, network access or learner volume
was involved.

The current 043 reference SHA256 is
`a456f9cda5557e2f51e8cb49edecdf34e7ec65e87f5279415585559e7a32ee79`.
The current 046 reference SHA256 is
`97670ff155a1292bea63c827691171d5734c3b2b6bea5c3b87362bb3a34ed91f`.
Earlier receipts for those two sources are historical and must not substitute
for these repaired-source proofs.

## Durable sources and scope

The six expert specifications and renderer live in
`courses/llm-theory/authoring/`. The full expert authoring entry point remains:

```text
python courses/llm-theory/authoring/build.py
```

The renderer incorporates `depth_reviews_foundations_expert.py`. For the 15
reviewed guides and explanatory prose only, use:

```text
python courses/llm-theory/authoring/review_guides.py
```

That narrower operation preserves fenced programs and does not edit learner
artifacts, executable references, shared inventories or the earlier generated
LLM batches. The directly maintained pilots 001-009 remain authoritative.
Root owns shared reader/navigation regeneration and final integration.

Java and all 42 JavaScript/TypeScript lessons are now authored and qualified;
the former 001-018 JavaScript boundary is obsolete. This checkpoint makes no
claim about GPU kernels, distributed serving, pretrained-model generalization,
native Windows execution or production deployment based on tiny CPU fixtures.

## Textbook follow-up: superseding numerical receipts

The final independent pass corrected046 online attention to reject nonfinite
accumulator/output state even when inputs and scores are finite. It corrected048
inverse-CDF sampling to preserve strictly positive support under rounding at the
upper boundary. Both current references and both sequential worked programs,
plus dedicated numerical regressions, passed current Core Docker in
work/llm-final-numeric-docker-acceptance.jsonl. The previous046 hash and receipt
above are historical. The portable runtime-reference-evidence.json now carries
the updated source identities. The separate code-change ledger preserves the
scope of the earlier prose-only parity receipt.

# BRIDGE-AI-01 — Solution reasoning

Start with the
[learner file](../lessons/bridge_ai_01_application_engineering.py). The
executable reference is
[bridge_ai_01_application_engineering_solution.py](bridge_ai_01_application_engineering_solution.py).

## Deterministic boundaries

`EmbeddingModel` and `TextModel` expose only behavior the orchestrator needs.
`KeywordEmbedding` produces fixed term-count vectors, while
`DeterministicAnswerModel` maps the first approved document ID to a reviewed
answer. Neither uses networking, a hosted SDK, an account, a credential, or
downloaded model weights.

This isolates application correctness from probabilistic model behavior.
Recording requests also makes instruction and context boundaries directly
assertable.

## Retrieval and authorization

`retrieve()` validates the query, embeds it once, and then filters each
document by audience, sensitivity, and obvious injection markers *before*
embedding the document. Positive-score candidates sort by descending score and
ascending ID. Selection enforces top-k and a total excerpt character budget.

The injection marker check is deliberately described as a quarantine heuristic.
The secure architecture does not depend on it being complete. Untrusted-data
serialization, restricted citations, no tool access, output validation, and
adversarial evaluation remain necessary.

## Request and output schemas

`build_request()` serializes each approved hit to one deterministic JSON line
with an explicit `untrusted_document_data` label. It estimates input size before
calling the model double.

`parse_structured_answer()` accepts only one object with exactly three fields.
It validates field types, unique citations, citation membership, and consistent
abstention. Invalid output fails closed as `UnsafeModelOutput`; no repair path
hides model-contract failures.

## Resource and leakage gates

`run_assistant()` checks estimated input before generation and reported input,
output, latency, and derived cost units afterward. Separate gates make failures
diagnosable. A blocked output-fragment check supplies a final exercise-level
leakage guard.

Unauthorized content is primarily stopped at retrieval. Output scanning is
defense in depth and should never be presented as a replacement for access
control and minimization.

## Evaluation reasoning

The evaluator computes one transparent value per dimension:

- citation recall is overlap with expected citation IDs;
- abstention accuracy compares the declared behavior;
- leakage rate counts forbidden-fragment appearances;
- budget pass rate checks all declared resource limits.

Exceptions caused by output or budget rejection receive zero citation credit
and do not count as a budget pass. A production evaluator would retain
per-case reasons and confidence intervals; this compact result keeps the first
lab inspectable.

## Tradeoffs

- Keyword vectors are interpretable and deterministic but cannot represent
  semantics. That is useful for orchestration tests, not search-quality claims.
- Filtering obvious injection text reduces exercise risk but can block benign
  discussion of security and miss paraphrased attacks.
- Taking the first ranked document makes model behavior auditable but does not
  synthesize several sources. Multi-source reasoning needs stronger citation
  and contradiction tests.
- Exact JSON validation improves reliability but can reduce completion rate.
  Retries or repair require their own bounds and evaluation.
- A character-to-token proxy is stable across machines but not provider-accurate.
- Abstract cost units keep the lesson provider-neutral. Real billing requires
  usage reports and versioned prices.
- Blocked fragments catch known markers but not semantic leakage.
- The compact evaluator averages cases equally. High-risk cases may need
  explicit gates rather than an average.

Before adding any external adapter, preserve these offline tests and add a
separately authorized integration suite covering network failure, timeouts,
rate limits, usage accounting, model-version drift, provider data policy, and
adversarial behavior.

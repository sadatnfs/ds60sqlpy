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


<!-- BEGIN BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->
## Small executable check

The local similarity boundary is deterministic and requires no model service:

```python
from bridge.professional.solutions.bridge_ai_01_application_engineering_solution import (
    cosine_similarity,
)

assert cosine_similarity((1.0, 0.0), (1.0, 0.0)) == 1.0
assert cosine_similarity((1.0, 0.0), (0.0, 1.0)) == 0.0
```

Separate tests should prove unauthorized document text never reaches the
recording embedding double.
<!-- END BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->

## Exercise solutions

These walkthroughs map one-for-one to the answer-free learner artifact and
companion guide. The executable reference is `bridge/professional/solutions/bridge_ai_01_application_engineering_solution.py`.

**Shared failure rule:** Retrieving unauthorized text, trusting model-shaped JSON, or reporting a passing toy evaluation as production safety evidence creates false assurance.

### Exercise 1 — Validation

**Prompt:** Validate every dataclass invariant for IDs, text, audiences, bounds, token/cost
budgets, and latency.

**Approach:** Use `__post_init__` checks for non-blank identifiers/text, non-empty audiences
where required, positive limits, finite non-negative scores/latency, and internally consistent
token budgets.

**Why:** Fail at construction so invalid state cannot cross later boundaries.

**Verification evidence:** Parameterize every dataclass with blank IDs/text, empty audiences, non-positive bounds, non-finite scores/latency, and inconsistent budgets; assert exact construction failures and one fully valid object per type.

### Exercise 2 — Math

**Prompt:** Implement cosine similarity with mismatched-dimension and zero-vector handling.

**Approach:** Require equal non-empty dimensions, compute dot product and Euclidean norms, and
reject zero norms instead of emitting NaN. Deterministic float comparison uses an explicit
tolerance.

**Why:** Validate shape and norms before division.

**Verification evidence:** Assert identical vectors score `1.0`, orthogonal vectors `0.0`, mismatched/empty dimensions and zero norms raise `ValueError`, and near-equal comparisons use the declared tolerance.

### Exercise 3 — Authorization testing

**Prompt:** Use a recording embedding double to prove sensitive, unauthorized, and quarantined
documents are filtered before embedding.

**Approach:** Filter policy first, then embed only query and approved documents. Assert
forbidden document text/IDs are absent from every recorded embed call.

**Why:** Call history is the evidence that prohibited text never crossed the adapter.

**Verification evidence:** Record embedding inputs for a mixed document set; assert the query and only authorized, non-sensitive, non-quarantined documents are embedded and forbidden text/IDs never cross the call boundary.

### Exercise 4 — Ranking

**Prompt:** Rank equal-score documents deterministically while enforcing top-k and total
context-character bounds.

**Approach:** Sort by score descending then document ID, skip/add excerpts until top-k or
context budget is reached, and return an immutable tuple in that order.

**Why:** Use a stable document ID tie-breaker and apply the character budget without splitting
trust rules.

**Verification evidence:** Give equal-score documents in reversed input order; assert ranking uses ascending document ID, returns at most `top_k`, and total selected excerpt characters never exceed the policy limit.

### Exercise 5 — Prompt boundary

**Prompt:** Serialize context as untrusted JSON containing only approved document IDs and
bounded excerpts.

**Approach:** Create a fixed system prompt that labels the JSON as untrusted evidence, serialize
only allowlisted fields, and never concatenate retrieved text into instruction prose.

**Why:** Separate system instructions, user query, and retrieved data structurally.

**Verification evidence:** Parse each serialized context line as JSON; assert exact approved ID/text fields plus the `untrusted_document_data` label, deterministic order, bounded excerpts, and no unauthorized field.

### Exercise 6 — Schema validation

**Prompt:** Implement exact structured-answer validation and test all malformed, extra-field,
wrong-type, duplicate-citation, and inconsistent-abstention cases.

**Approach:** Require exactly `answer`, `citations`, and `abstained`; validate types, unique
strings, allowed citation membership, and consistent empty-answer/citation behavior for
abstention.

**Why:** Parsing JSON is only the first step; validate exact shape and semantics.

**Verification evidence:** Parameterize missing/extra fields, wrong types, duplicate/unknown citations, and inconsistent abstention; assert all raise `UnsafeModelOutput` while one exact valid object is accepted unchanged.

### Exercise 7 — Adversarial testing

**Prompt:** Use a malicious model double that cites an unretrieved document and prove validation
rejects it.

**Approach:** Return valid-looking JSON with a foreign ID, pass only retrieved IDs to the
parser, and assert a closed failure before constructing `AssistantRun`.

**Why:** Citations are authorization claims and must be a subset of retrieved evidence.

**Verification evidence:** Return a citation ID absent from retrieved hits; assert parsing/orchestration raises `UnsafeModelOutput`, produces no accepted answer, and records the invalid model call once.

### Exercise 8 — Leakage

**Prompt:** Return a blocked private marker from the model and prove the output boundary fails
closed without logging the answer.

**Approach:** Scan the parsed answer for configured blocked fragments, raise a safe error, and
capture all logs to show neither raw response nor marker is emitted.

**Why:** Leakage inspection occurs after parsing but before return/logging.

**Verification evidence:** Return a configured private marker; assert the run fails closed, the marker is absent from logs and returned objects, and only a bounded error class/outcome is observable.

### Exercise 9 — Budgets

**Prompt:** Test preflight input, actual input, output, cost-unit, and latency budget failures
separately.

**Approach:** Construct one double per boundary that exceeds only that value; require a stable
safe error and prove no later adapter/effect runs after a preflight failure.

**Why:** Each limit is independent evidence and needs its own failure case.

**Verification evidence:** Trigger estimated-input, reported-input, output, cost-unit, and latency limits one at a time; assert each raises `BudgetExceeded` at its named gate and unaffected limits still pass.

### Exercise 10 — Evaluation

**Prompt:** Add deterministic grounded, abstention, injection-document, and
unauthorized-private-document cases.

**Approach:** Define checked-in cases with explicit citation sets/abstention flags, run the same
offline runner, and calculate citation recall, abstention accuracy, leakage rate, and budget
pass rate.

**Why:** Expected citations and forbidden fragments make safety assertions inspectable.

**Verification evidence:** Run grounded, abstention, injection-document, and unauthorized-private cases; compare exact citations/abstention, zero forbidden fragments, expected adapter calls, and per-case budget outcome.

### Exercise 11 — Evidence limits

**Prompt:** Explain which safety claims deterministic doubles prove and which require a
separately authorized real-adapter evaluation.

**Approach:** Doubles prove filtering order, schema/budget/leakage gates, and metric math. They
do not prove model quality, provider privacy, latency distribution, token accounting,
adversarial coverage, or production authorization configuration.

**Why:** A controlled harness proves orchestration, not provider behavior or real-world
robustness.

**Verification evidence:** Provide a two-column claim table: deterministic doubles prove orchestration/call order/schema gates; provider reliability, real model quality, billing, privacy policy, and adversarial robustness remain unproved.

### Exercise 12 — Prompt injection

**Prompt:** Insert retrieved text that says to ignore policy and reveal secrets; prove it stays
data and cannot change allowed citations.

**Approach:** Keep the malicious document authorized only for the test, serialize it under the
untrusted context field, and require citations/output to satisfy the same parser and
blocked-fragment checks.

**Why:** The model double should attempt the attack so downstream validation is exercised.

**Verification evidence:** Insert an instruction-attack document and configure the model to follow it if seen; assert the document is quarantined or serialized only as data and allowed citations/output policy cannot expand.

### Exercise 13 — Text normalization

**Prompt:** Choose normalization rules for blank IDs, Unicode text, and blocked-fragment
matching without silently changing document meaning.

**Approach:** Trim identifiers, preserve original evidence text, and apply a documented
case/Unicode normalization only to comparison keys or leakage scans. Test confusable/combining
forms explicitly.

**Why:** Normalization can close bypasses but can also merge distinct content.

**Verification evidence:** Test whitespace-only IDs, composed/decomposed Unicode, and case/normalization variants of blocked markers; document which normalize to equality and which remain distinct without altering source meaning.

### Exercise 14 — Numeric determinism

**Prompt:** Test equal and nearly equal embedding scores with a declared tolerance and
deterministic tie-breaker.

**Approach:** Treat the computed float as the primary key and document exact/tolerance policy;
always use document ID as final deterministic ordering evidence.

**Why:** Do not rely on platform-specific incidental sort order.

**Verification evidence:** Rank equal and epsilon-different scores under the declared tolerance; assert deterministic ID tie-breaking and identical order across repeated runs.

### Exercise 15 — Token estimation

**Prompt:** Design a conservative preflight token estimator and explain why it cannot replace
actual adapter accounting.

**Approach:** Estimate from bounded character counts plus fixed prompt overhead with a safety
margin; after generation, enforce the model response's actual token counts independently.

**Why:** Preflight should fail early on obvious excess and leave headroom.

**Verification evidence:** For representative strings, record the conservative estimated token count and headroom; assert obvious oversize input fails preflight and actual adapter usage remains the authoritative post-call value.

### Exercise 16 — Adapter failure

**Prompt:** Classify embedding/model timeout and provider-like errors without retrying unsafe or
permanent failures.

**Approach:** Map only explicitly transient adapter errors to bounded retry owned outside the
pure orchestration; schema, authorization, leakage, and budget failures escape immediately.

**Why:** Offline doubles can model exception classes and call order.

**Verification evidence:** Configure timeout/transient/permanent/unsafe-output exceptions; assert only the explicitly retryable adapter class is retried within its bound and permanent or unsafe failures have one call.

### Exercise 17 — Abstention

**Prompt:** Require abstention when no authorized evidence survives retrieval and test that the
text model is not called.

**Approach:** Return or construct the documented abstention with empty citations before request
generation, or raise a defined no-evidence result; assert zero model calls.

**Why:** No evidence is a deterministic pre-model decision.

**Verification evidence:** Use a query with no authorized hit; assert an abstaining `AssistantRun` is returned (or the declared abstention path), citations are empty, and text-model call count is zero.

### Exercise 18 — Observability

**Prompt:** Design safe logs/metrics that exclude user query, context, embeddings, and raw model
output.

**Approach:** Log a correlation ID and approved document IDs only if policy allows; metrics use
fixed stage/outcome tags and numeric token/latency values. Test sentinels across every omitted
content channel.

**Why:** Use bounded stage/outcome/error-class metadata only.

**Verification evidence:** Capture logs and metrics for pass/failure; assert only bounded stage/outcome/error-class/count fields appear and query, context, embeddings, raw output, document IDs, and credentials are absent.

### Exercise 19 — Metric edge cases

**Prompt:** Define evaluation metrics for an empty case set and zero expected citations without
divide-by-zero ambiguity.

**Approach:** Reject an empty evaluation suite; treat a case with no expected citations as
recall-not-applicable or one only under an explicit convention, then aggregate with documented
denominators.

**Why:** Denominators and conventions belong in the metric contract.

**Verification evidence:** Evaluate an empty case set and a case with zero expected citations; assert documented finite metric values with no division error or NaN and retain the denominator in results.

### Exercise 20 — Regression gates

**Prompt:** Set deterministic pass thresholds for citation recall, abstention accuracy, leakage,
and budgets without hiding per-case failures.

**Approach:** Require leakage rate zero and explicit minimums for other metrics; emit failing
case IDs/reasons in bounded test output so one regression cannot be averaged away.

**Why:** Aggregate gates complement, not replace, case-level evidence.

**Verification evidence:** Apply explicit citation-recall, abstention, leakage-zero, and budget thresholds; assert one failing case remains visible even if aggregate averages would otherwise pass.

### Exercise 21 — Real adapter boundary

**Prompt:** Design an optional hosted adapter evaluation that keeps credentials external and
never weakens the offline default.

**Approach:** Read a provider key only inside the adapter process, gate execution with a
separate flag, use synthetic authorized data, bound cost/time, redact outputs, and label results
as provider-specific evidence.

**Why:** Network, cost, and data authorization require an explicit opt-in gate.

**Verification evidence:** Specify an opt-in environment flag, external credential source, bounded dataset/cost/time, adapter version record, and cleanup; assert the normal test command cannot import/call the hosted adapter.

### Exercise 22 — Threat model

**Prompt:** Write residual risks for retrieval poisoning, embedding inversion, model
memorization, authorization drift, and evaluator blind spots.

**Approach:** Map each threat to current control, missing evidence, owner, and stop condition.
Explicitly state that deterministic local tests cannot establish absence of unknown attacks.

**Why:** Controls reduce specific risks; they do not make a universal safety claim.

**Verification evidence:** Produce residual-risk rows for retrieval poisoning, embedding inversion, memorization, authorization drift, and evaluator blind spots, each with owner, current control, detection evidence, and next action.

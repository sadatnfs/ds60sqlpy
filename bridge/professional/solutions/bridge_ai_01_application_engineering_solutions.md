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

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 2 — Math

**Prompt:** Implement cosine similarity with mismatched-dimension and zero-vector handling.

**Approach:** Require equal non-empty dimensions, compute dot product and Euclidean norms, and
reject zero norms instead of emitting NaN. Deterministic float comparison uses an explicit
tolerance.

**Why:** Validate shape and norms before division.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 3 — Authorization testing

**Prompt:** Use a recording embedding double to prove sensitive, unauthorized, and quarantined
documents are filtered before embedding.

**Approach:** Filter policy first, then embed only query and approved documents. Assert
forbidden document text/IDs are absent from every recorded embed call.

**Why:** Call history is the evidence that prohibited text never crossed the adapter.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 4 — Ranking

**Prompt:** Rank equal-score documents deterministically while enforcing top-k and total
context-character bounds.

**Approach:** Sort by score descending then document ID, skip/add excerpts until top-k or
context budget is reached, and return an immutable tuple in that order.

**Why:** Use a stable document ID tie-breaker and apply the character budget without splitting
trust rules.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 5 — Prompt boundary

**Prompt:** Serialize context as untrusted JSON containing only approved document IDs and
bounded excerpts.

**Approach:** Create a fixed system prompt that labels the JSON as untrusted evidence, serialize
only allowlisted fields, and never concatenate retrieved text into instruction prose.

**Why:** Separate system instructions, user query, and retrieved data structurally.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 6 — Schema validation

**Prompt:** Implement exact structured-answer validation and test all malformed, extra-field,
wrong-type, duplicate-citation, and inconsistent-abstention cases.

**Approach:** Require exactly `answer`, `citations`, and `abstained`; validate types, unique
strings, allowed citation membership, and consistent empty-answer/citation behavior for
abstention.

**Why:** Parsing JSON is only the first step; validate exact shape and semantics.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 7 — Adversarial testing

**Prompt:** Use a malicious model double that cites an unretrieved document and prove validation
rejects it.

**Approach:** Return valid-looking JSON with a foreign ID, pass only retrieved IDs to the
parser, and assert a closed failure before constructing `AssistantRun`.

**Why:** Citations are authorization claims and must be a subset of retrieved evidence.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 8 — Leakage

**Prompt:** Return a blocked private marker from the model and prove the output boundary fails
closed without logging the answer.

**Approach:** Scan the parsed answer for configured blocked fragments, raise a safe error, and
capture all logs to show neither raw response nor marker is emitted.

**Why:** Leakage inspection occurs after parsing but before return/logging.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 9 — Budgets

**Prompt:** Test preflight input, actual input, output, cost-unit, and latency budget failures
separately.

**Approach:** Construct one double per boundary that exceeds only that value; require a stable
safe error and prove no later adapter/effect runs after a preflight failure.

**Why:** Each limit is independent evidence and needs its own failure case.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 10 — Evaluation

**Prompt:** Add deterministic grounded, abstention, injection-document, and
unauthorized-private-document cases.

**Approach:** Define checked-in cases with explicit citation sets/abstention flags, run the same
offline runner, and calculate citation recall, abstention accuracy, leakage rate, and budget
pass rate.

**Why:** Expected citations and forbidden fragments make safety assertions inspectable.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 11 — Evidence limits

**Prompt:** Explain which safety claims deterministic doubles prove and which require a
separately authorized real-adapter evaluation.

**Approach:** Doubles prove filtering order, schema/budget/leakage gates, and metric math. They
do not prove model quality, provider privacy, latency distribution, token accounting,
adversarial coverage, or production authorization configuration.

**Why:** A controlled harness proves orchestration, not provider behavior or real-world
robustness.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 12 — Prompt injection

**Prompt:** Insert retrieved text that says to ignore policy and reveal secrets; prove it stays
data and cannot change allowed citations.

**Approach:** Keep the malicious document authorized only for the test, serialize it under the
untrusted context field, and require citations/output to satisfy the same parser and
blocked-fragment checks.

**Why:** The model double should attempt the attack so downstream validation is exercised.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 13 — Text normalization

**Prompt:** Choose normalization rules for blank IDs, Unicode text, and blocked-fragment
matching without silently changing document meaning.

**Approach:** Trim identifiers, preserve original evidence text, and apply a documented
case/Unicode normalization only to comparison keys or leakage scans. Test confusable/combining
forms explicitly.

**Why:** Normalization can close bypasses but can also merge distinct content.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 14 — Numeric determinism

**Prompt:** Test equal and nearly equal embedding scores with a declared tolerance and
deterministic tie-breaker.

**Approach:** Treat the computed float as the primary key and document exact/tolerance policy;
always use document ID as final deterministic ordering evidence.

**Why:** Do not rely on platform-specific incidental sort order.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 15 — Token estimation

**Prompt:** Design a conservative preflight token estimator and explain why it cannot replace
actual adapter accounting.

**Approach:** Estimate from bounded character counts plus fixed prompt overhead with a safety
margin; after generation, enforce the model response's actual token counts independently.

**Why:** Preflight should fail early on obvious excess and leave headroom.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 16 — Adapter failure

**Prompt:** Classify embedding/model timeout and provider-like errors without retrying unsafe or
permanent failures.

**Approach:** Map only explicitly transient adapter errors to bounded retry owned outside the
pure orchestration; schema, authorization, leakage, and budget failures escape immediately.

**Why:** Offline doubles can model exception classes and call order.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 17 — Abstention

**Prompt:** Require abstention when no authorized evidence survives retrieval and test that the
text model is not called.

**Approach:** Return or construct the documented abstention with empty citations before request
generation, or raise a defined no-evidence result; assert zero model calls.

**Why:** No evidence is a deterministic pre-model decision.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 18 — Observability

**Prompt:** Design safe logs/metrics that exclude user query, context, embeddings, and raw model
output.

**Approach:** Log a correlation ID and approved document IDs only if policy allows; metrics use
fixed stage/outcome tags and numeric token/latency values. Test sentinels across every omitted
content channel.

**Why:** Use bounded stage/outcome/error-class metadata only.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 19 — Metric edge cases

**Prompt:** Define evaluation metrics for an empty case set and zero expected citations without
divide-by-zero ambiguity.

**Approach:** Reject an empty evaluation suite; treat a case with no expected citations as
recall-not-applicable or one only under an explicit convention, then aggregate with documented
denominators.

**Why:** Denominators and conventions belong in the metric contract.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 20 — Regression gates

**Prompt:** Set deterministic pass thresholds for citation recall, abstention accuracy, leakage,
and budgets without hiding per-case failures.

**Approach:** Require leakage rate zero and explicit minimums for other metrics; emit failing
case IDs/reasons in bounded test output so one regression cannot be averaged away.

**Why:** Aggregate gates complement, not replace, case-level evidence.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 21 — Real adapter boundary

**Prompt:** Design an optional hosted adapter evaluation that keeps credentials external and
never weakens the offline default.

**Approach:** Read a provider key only inside the adapter process, gate execution with a
separate flag, use synthetic authorized data, bound cost/time, redact outputs, and label results
as provider-specific evidence.

**Why:** Network, cost, and data authorization require an explicit opt-in gate.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 22 — Threat model

**Prompt:** Write residual risks for retrieval poisoning, embedding inversion, model
memorization, authorization drift, and evaluator blind spots.

**Approach:** Map each threat to current control, missing evidence, owner, and stop condition.
Explicitly state that deterministic local tests cannot establish absence of unknown attacks.

**Why:** Controls reduce specific risks; they do not make a universal safety claim.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

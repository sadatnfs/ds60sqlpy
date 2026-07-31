# BRIDGE-AI-01 — Offline AI application engineering

## Level and prerequisites

**Level:** Advanced  
**Stable lesson ID:** `bridge-ai-01`  
**Catalog prerequisites:** `bridge-08` and `python-test-01`  
**Prerequisites:** [Bridge Day 8](../../companion-guides/day08_production_capstone.md)
and the
[professional testing module](../../../python/professional/companion-guides/py_test_01_architecture_generative.md).
Python Day 15 and Bridge Day 5 are earlier background within those paths.

This module teaches the engineering boundaries around a retrieval-augmented
assistant without requiring or contacting a hosted model. Both “embedding” and
“generation” are deterministic local doubles. There is no model SDK, account,
network call, API key, downloaded weight, or hidden usage charge.

Run the learner file:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\lessons\bridge_ai_01_application_engineering.py
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/lessons/bridge_ai_01_application_engineering.py
```

The reference implementation and its evaluation also run offline:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\solutions\bridge_ai_01_application_engineering_solution.py
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/solutions/bridge_ai_01_application_engineering_solution.py
```


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\lessons\bridge_ai_01_application_engineering.py
.\.venv\Scripts\python.exe -m pytest bridge\professional\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/lessons/bridge_ai_01_application_engineering.py
.venv/bin/python -m pytest bridge/professional/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/professional/lessons/bridge_ai_01_application_engineering.py`, and use small fakes or recording doubles for the
default evidence path. This lesson is fully offline: use the checked-in model doubles. It needs no PostgreSQL server, hosted model, SDK account, API key, network call, or downloaded model weights.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Learning objectives

By the end, you can:

- define small embedding and text-model Protocols;
- replace nondeterministic model calls with controlled local doubles;
- enforce document authorization before embedding or ranking;
- rank evidence deterministically with a top-k and character bound;
- keep retrieved text in an untrusted-data boundary;
- validate exact structured-output fields, types, citations, and abstention;
- block citations outside the approved retrieval set;
- prevent obvious prompt-injection content from entering context while
  recognizing the limits of keyword detection;
- add output leakage checks as defense in depth;
- enforce input-token, output-token, latency, and cost-unit budgets;
- evaluate citation recall, abstention, leakage, and resource compliance on a
  checked-in dataset.

## Vocabulary and concepts

| Term | Meaning |
|---|---|
| embedding | Numeric representation used here only for deterministic similarity |
| model double | Local fake or stub implementing the same boundary as a model |
| retrieval | Selecting bounded evidence relevant to a query |
| cosine similarity | Angle-based comparison between equal-length vectors |
| top-k | Maximum number of ranked documents admitted to context |
| prompt injection | Untrusted text attempting to act as instructions |
| data leakage | Information crossing an authorization or output boundary |
| structured output | Machine-validated object rather than free-form prose |
| citation grounding | Restricting claimed evidence to retrieved document IDs |
| abstention | Explicitly declining when approved evidence is insufficient |
| evaluation dataset | Versioned cases with expected behavior and safety checks |
| token proxy | Deterministic local estimate used for this offline budget lab |
| cost unit | Provider-independent teaching unit derived from input/output usage |
| latency budget | Maximum acceptable end-to-end model response time |
| fail closed | Rejecting uncertain output instead of silently accepting it |

## Worked example / walkthrough

### 1. Begin with narrow Protocols

The application owns two small contracts:

```python
class EmbeddingModel(Protocol):
    def embed(self, text: str) -> Sequence[float]: ...


class TextModel(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse: ...
```

Business logic does not import a hosted client. Tests can inject a keyword
embedding and a deterministic answer mapping. If a real adapter is ever added,
it must satisfy the same contracts and all existing safety tests.

### 2. Authorize before processing content

The retrieval order is a security invariant:

```text
audience and sensitivity filter
    -> obvious-injection quarantine
    -> embedding
    -> similarity ranking
    -> top-k and character bounds
```

Filtering after embedding is too late: an unauthorized document has already
crossed into another processing system. The tests use a recording embedding
double to prove that private text is never passed to `embed()`.

`audiences` demonstrates a simple policy seam; real authorization may depend
on user identity, tenant, document ACL version, purpose, retention, and legal
policy. Cache keys must include every authorization dimension or cached
retrieval can leak across callers.

### 3. Bound retrieval deterministically

The solution ranks positive cosine similarity by:

1. score descending;
2. document ID ascending as a stable tie-breaker.

It admits at most `top_k` hits and at most `max_context_characters` across
excerpts. Bounds control memory, latency, and downstream cost. They also make
tests reproducible.

The keyword embedding is deliberately not “intelligent.” It turns a fixed
vocabulary into term-count vectors. That is enough to test ranking,
authorization order, zero-vector behavior, tie-breaking, and context bounds.

### 4. Treat retrieved documents as untrusted data

Retrieved text can contain instructions such as “ignore previous rules.” The
request builder serializes every hit as JSON with:

```json
{"document_id":"course-db","text":"...","trust":"untrusted_document_data"}
```

The system boundary states that document text is data, citations must come from
the supplied IDs, and insufficient evidence requires abstention.

The exercise also quarantines several obvious attack phrases before context
construction. This heuristic is defense in depth, not a complete detector:
attackers can paraphrase, encode, translate, or split instructions. The primary
controls are authorization, instruction/data separation, tool restrictions,
output validation, least privilege, and evaluation with adversarial cases.

### 5. Validate output as a schema

The model double must return exactly:

```json
{
  "answer": "Non-empty text",
  "citations": ["approved-document-id"],
  "abstained": false
}
```

Validation rejects:

- invalid JSON or a non-object root;
- missing or extra keys;
- wrong field types;
- duplicate citations;
- citations outside the retrieved set;
- an abstention that claims citations;
- a substantive answer without citations.

The parser does not “repair” invalid output. Silent repair makes evaluation and
security behavior hard to see.

### 6. Add a leakage boundary

The strongest protection is preventing unauthorized content from entering
retrieval. A case-specific output blocklist is a final backstop in this local
lab. If a forbidden fragment appears, the run fails closed.

Do not treat a blocklist as a general privacy solution. Real systems need data
classification, authorization, minimization, logging restrictions, retention,
human review for high-risk actions, and incident response. Logs should record
safe IDs, counts, timing, outcome, and error type—not prompts, documents, model
output, credentials, or private records.

### 7. Enforce cost and latency budgets

The offline model reports input tokens, output tokens, and latency. The
orchestrator checks:

- estimated input before generation;
- actual input after generation;
- actual output;
- latency;
- cost units: `input * input_rate + output * output_rate`.

This lab uses a deterministic character-based token proxy and abstract cost
units. A real adapter must use provider-reported usage and a versioned price
configuration. Never claim exact billing from a character heuristic.

Budget failures raise a distinct exception. The caller can abstain, use a
smaller context, route to a cheaper approved adapter, or return a controlled
error; it should not silently remove safety instructions.

### 8. Evaluate behavior, not a demo transcript

Each `EvaluationCase` declares:

- a stable case ID and query;
- expected citation IDs;
- whether the answer should abstain;
- forbidden output fragments.

The evaluator reports:

- citation recall;
- abstention accuracy;
- leakage rate;
- budget pass rate.

Keep the dataset checked in, reviewed, small, and free of real personal or
confidential data. Add cases for zero evidence, ambiguous evidence, injection
text, unauthorized documents, malformed output, unauthorized citations, and
budget boundaries.

Accuracy alone is insufficient. A system can answer many questions while
leaking data, inventing citations, or exceeding its service budget.

### 9. Understand what this module does not claim

The local doubles prove application composition, not model quality. They cannot
prove that a hosted model follows instructions, that a tokenizer matches the
proxy, or that an external service meets latency and privacy terms.

Adding a real adapter is a separate, opt-in specialization requiring explicit
authorization, dependency and secret management, network disclosure, provider
terms, data handling review, rate limits, retries, telemetry policy, and
integration evaluation. None of that belongs in the default offline path.

## Exercises

### Practice contract

- **Focus:** Build an offline, deterministic retrieval-and-generation boundary with authorization-before-embedding, untrusted context, exact output schemas, budgets, leakage checks, and evaluation.
- **Assumptions:** Documents, embedding/model adapters, and evaluation cases are local deterministic doubles; no API key, hosted service, or network call is required.
- **Primary failure mode:** Retrieving unauthorized text, trusting model-shaped JSON, or reporting a passing toy evaluation as production safety evidence creates false assurance.
- **Evidence loop:** state the boundary and prediction, implement against
  deterministic local doubles, test success/failure/cleanup, and label any
  optional live-adapter evidence separately from offline proof.

1. **Validation:** Validate every dataclass invariant for IDs, text, audiences, bounds,
   token/cost budgets, and latency.
   - **Progressive hint:** Fail at construction so invalid state cannot cross later boundaries.
   - **Verify:** Parameterize every dataclass with blank IDs/text, empty audiences, non-positive bounds, non-finite scores/latency, and inconsistent budgets; assert exact construction failures and one fully valid object per type.
2. **Math:** Implement cosine similarity with mismatched-dimension and zero-vector handling.
   - **Progressive hint:** Validate shape and norms before division.
   - **Verify:** Assert identical vectors score `1.0`, orthogonal vectors `0.0`, mismatched/empty dimensions and zero norms raise `ValueError`, and near-equal comparisons use the declared tolerance.
3. **Authorization testing:** Use a recording embedding double to prove sensitive, unauthorized,
   and quarantined documents are filtered before embedding.
   - **Progressive hint:** Call history is the evidence that prohibited text never crossed the
     adapter.
   - **Verify:** Record embedding inputs for a mixed document set; assert the query and only authorized, non-sensitive, non-quarantined documents are embedded and forbidden text/IDs never cross the call boundary.
4. **Ranking:** Rank equal-score documents deterministically while enforcing top-k and total
   context-character bounds.
   - **Progressive hint:** Use a stable document ID tie-breaker and apply the character budget
     without splitting trust rules.
   - **Verify:** Give equal-score documents in reversed input order; assert ranking uses ascending document ID, returns at most `top_k`, and total selected excerpt characters never exceed the policy limit.
5. **Prompt boundary:** Serialize context as untrusted JSON containing only approved document
   IDs and bounded excerpts.
   - **Progressive hint:** Separate system instructions, user query, and retrieved data
     structurally.
   - **Verify:** Parse each serialized context line as JSON; assert exact approved ID/text fields plus the `untrusted_document_data` label, deterministic order, bounded excerpts, and no unauthorized field.
6. **Schema validation:** Implement exact structured-answer validation and test all malformed,
   extra-field, wrong-type, duplicate-citation, and inconsistent-abstention cases.
   - **Progressive hint:** Parsing JSON is only the first step; validate exact shape and
     semantics.
   - **Verify:** Parameterize missing/extra fields, wrong types, duplicate/unknown citations, and inconsistent abstention; assert all raise `UnsafeModelOutput` while one exact valid object is accepted unchanged.
7. **Adversarial testing:** Use a malicious model double that cites an unretrieved document and
   prove validation rejects it.
   - **Progressive hint:** Citations are authorization claims and must be a subset of retrieved
     evidence.
   - **Verify:** Return a citation ID absent from retrieved hits; assert parsing/orchestration raises `UnsafeModelOutput`, produces no accepted answer, and records the invalid model call once.
8. **Leakage:** Return a blocked private marker from the model and prove the output boundary
   fails closed without logging the answer.
   - **Progressive hint:** Leakage inspection occurs after parsing but before return/logging.
   - **Verify:** Return a configured private marker; assert the run fails closed, the marker is absent from logs and returned objects, and only a bounded error class/outcome is observable.
9. **Budgets:** Test preflight input, actual input, output, cost-unit, and latency budget
   failures separately.
   - **Progressive hint:** Each limit is independent evidence and needs its own failure case.
   - **Verify:** Trigger estimated-input, reported-input, output, cost-unit, and latency limits one at a time; assert each raises `BudgetExceeded` at its named gate and unaffected limits still pass.
10. **Evaluation:** Add deterministic grounded, abstention, injection-document, and
   unauthorized-private-document cases.
   - **Progressive hint:** Expected citations and forbidden fragments make safety assertions
     inspectable.
   - **Verify:** Run grounded, abstention, injection-document, and unauthorized-private cases; compare exact citations/abstention, zero forbidden fragments, expected adapter calls, and per-case budget outcome.
11. **Evidence limits:** Explain which safety claims deterministic doubles prove and which
   require a separately authorized real-adapter evaluation.
   - **Progressive hint:** A controlled harness proves orchestration, not provider behavior or
     real-world robustness.
   - **Verify:** Provide a two-column claim table: deterministic doubles prove orchestration/call order/schema gates; provider reliability, real model quality, billing, privacy policy, and adversarial robustness remain unproved.
12. **Prompt injection:** Insert retrieved text that says to ignore policy and reveal secrets;
   prove it stays data and cannot change allowed citations.
   - **Progressive hint:** The model double should attempt the attack so downstream validation
     is exercised.
   - **Verify:** Insert an instruction-attack document and configure the model to follow it if seen; assert the document is quarantined or serialized only as data and allowed citations/output policy cannot expand.
13. **Text normalization:** Choose normalization rules for blank IDs, Unicode text, and
   blocked-fragment matching without silently changing document meaning.
   - **Progressive hint:** Normalization can close bypasses but can also merge distinct content.
   - **Verify:** Test whitespace-only IDs, composed/decomposed Unicode, and case/normalization variants of blocked markers; document which normalize to equality and which remain distinct without altering source meaning.
14. **Numeric determinism:** Test equal and nearly equal embedding scores with a declared
   tolerance and deterministic tie-breaker.
   - **Progressive hint:** Do not rely on platform-specific incidental sort order.
   - **Verify:** Rank equal and epsilon-different scores under the declared tolerance; assert deterministic ID tie-breaking and identical order across repeated runs.
15. **Token estimation:** Design a conservative preflight token estimator and explain why it
   cannot replace actual adapter accounting.
   - **Progressive hint:** Preflight should fail early on obvious excess and leave headroom.
   - **Verify:** For representative strings, record the conservative estimated token count and headroom; assert obvious oversize input fails preflight and actual adapter usage remains the authoritative post-call value.
16. **Adapter failure:** Classify embedding/model timeout and provider-like errors without
   retrying unsafe or permanent failures.
   - **Progressive hint:** Offline doubles can model exception classes and call order.
   - **Verify:** Configure timeout/transient/permanent/unsafe-output exceptions; assert only the explicitly retryable adapter class is retried within its bound and permanent or unsafe failures have one call.
17. **Abstention:** Require abstention when no authorized evidence survives retrieval and test
   that the text model is not called.
   - **Progressive hint:** No evidence is a deterministic pre-model decision.
   - **Verify:** Use a query with no authorized hit; assert an abstaining `AssistantRun` is returned (or the declared abstention path), citations are empty, and text-model call count is zero.
18. **Observability:** Design safe logs/metrics that exclude user query, context, embeddings,
   and raw model output.
   - **Progressive hint:** Use bounded stage/outcome/error-class metadata only.
   - **Verify:** Capture logs and metrics for pass/failure; assert only bounded stage/outcome/error-class/count fields appear and query, context, embeddings, raw output, document IDs, and credentials are absent.
19. **Metric edge cases:** Define evaluation metrics for an empty case set and zero expected
   citations without divide-by-zero ambiguity.
   - **Progressive hint:** Denominators and conventions belong in the metric contract.
   - **Verify:** Evaluate an empty case set and a case with zero expected citations; assert documented finite metric values with no division error or NaN and retain the denominator in results.
20. **Regression gates:** Set deterministic pass thresholds for citation recall, abstention
   accuracy, leakage, and budgets without hiding per-case failures.
   - **Progressive hint:** Aggregate gates complement, not replace, case-level evidence.
   - **Verify:** Apply explicit citation-recall, abstention, leakage-zero, and budget thresholds; assert one failing case remains visible even if aggregate averages would otherwise pass.
21. **Real adapter boundary:** Design an optional hosted adapter evaluation that keeps
   credentials external and never weakens the offline default.
   - **Progressive hint:** Network, cost, and data authorization require an explicit opt-in
     gate.
   - **Verify:** Specify an opt-in environment flag, external credential source, bounded dataset/cost/time, adapter version record, and cleanup; assert the normal test command cannot import/call the hosted adapter.
22. **Threat model:** Write residual risks for retrieval poisoning, embedding inversion, model
   memorization, authorization drift, and evaluator blind spots.
   - **Progressive hint:** Controls reduce specific risks; they do not make a universal safety
     claim.
   - **Verify:** Produce residual-risk rows for retrieval poisoning, embedding inversion, memorization, authorization drift, and evaluator blind spots, each with owner, current control, detection evidence, and next action.

### Before opening the solution

- Record what the offline doubles prove and what they cannot prove.
- Inspect exact call order, parameters, schema, and failure behavior.
- Keep credentials, payloads, and high-cardinality identifiers out of output.
- Require deterministic reruns before considering an exercise complete.


## Self-check

- Does authorization occur before embedding?
- Can a sensitive or wrong-audience document appear in a model request?
- Are retrieval count and total characters bounded?
- Is tie-breaking deterministic?
- Does the request label document content as untrusted data?
- Can output cite an ID that was not retrieved?
- Is malformed structured output rejected rather than repaired?
- Does no-evidence behavior abstain?
- Are input, output, latency, and cost checked independently?
- Does the evaluation dataset include safety and resource outcomes, not only
  answer quality?
- Are prompts, documents, model output, private markers, and credentials absent
  from logs?
- Can every default test run with networking disabled?
- Are there zero hosted SDKs, API keys, accounts, or downloaded weights?

## Common pitfalls

- **Embedding before authorization:** unauthorized content has already crossed a
  boundary.
- **Caching without authorization dimensions:** one caller can receive another
  caller's retrieval result.
- **Calling retrieved text “trusted”:** storage location does not make document
  instructions safe.
- **Depending on injection keywords alone:** attacks can be paraphrased.
- **Allowing arbitrary citations:** a plausible ID can create false grounding.
- **Repairing malformed output silently:** failures disappear from evaluation.
- **Treating an output blocklist as privacy:** prevention and authorization are
  stronger than post-generation scanning.
- **Using unlimited context:** cost, latency, and attack surface grow together.
- **Estimating provider billing from characters:** the local proxy is only a
  deterministic exercise mechanism.
- **Testing only one happy prompt:** behavior changes across evidence,
  abstention, malformed output, and attacks.
- **Logging complete prompts and outputs:** observability can become a leakage
  path.
- **Equating a fake with model validation:** doubles validate orchestration, not
  external model behavior.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-08`, `python-test-01`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-ai-01: AI Application Engineering with Deterministic Test Doubles.
Direct catalog prerequisites: bridge-08, python-test-01. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/professional/companion-guides/bridge_ai_01_application_engineering.md
Learner artifact: bridge/professional/lessons/bridge_ai_01_application_engineering.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

Complete the
[learner file](../lessons/bridge_ai_01_application_engineering.py) and your own
adversarial cases before reviewing the
[reference implementation](../solutions/bridge_ai_01_application_engineering_solution.py)
and [solution reasoning](../solutions/bridge_ai_01_application_engineering_solutions.md).
Then apply the same boundary-first design to a local document set whose
classification and license are known.

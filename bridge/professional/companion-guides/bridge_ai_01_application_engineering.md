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
2. **Math:** Implement cosine similarity with mismatched-dimension and zero-vector handling.
   - **Progressive hint:** Validate shape and norms before division.
3. **Authorization testing:** Use a recording embedding double to prove sensitive, unauthorized,
   and quarantined documents are filtered before embedding.
   - **Progressive hint:** Call history is the evidence that prohibited text never crossed the
     adapter.
4. **Ranking:** Rank equal-score documents deterministically while enforcing top-k and total
   context-character bounds.
   - **Progressive hint:** Use a stable document ID tie-breaker and apply the character budget
     without splitting trust rules.
5. **Prompt boundary:** Serialize context as untrusted JSON containing only approved document
   IDs and bounded excerpts.
   - **Progressive hint:** Separate system instructions, user query, and retrieved data
     structurally.
6. **Schema validation:** Implement exact structured-answer validation and test all malformed,
   extra-field, wrong-type, duplicate-citation, and inconsistent-abstention cases.
   - **Progressive hint:** Parsing JSON is only the first step; validate exact shape and
     semantics.
7. **Adversarial testing:** Use a malicious model double that cites an unretrieved document and
   prove validation rejects it.
   - **Progressive hint:** Citations are authorization claims and must be a subset of retrieved
     evidence.
8. **Leakage:** Return a blocked private marker from the model and prove the output boundary
   fails closed without logging the answer.
   - **Progressive hint:** Leakage inspection occurs after parsing but before return/logging.
9. **Budgets:** Test preflight input, actual input, output, cost-unit, and latency budget
   failures separately.
   - **Progressive hint:** Each limit is independent evidence and needs its own failure case.
10. **Evaluation:** Add deterministic grounded, abstention, injection-document, and
   unauthorized-private-document cases.
   - **Progressive hint:** Expected citations and forbidden fragments make safety assertions
     inspectable.
11. **Evidence limits:** Explain which safety claims deterministic doubles prove and which
   require a separately authorized real-adapter evaluation.
   - **Progressive hint:** A controlled harness proves orchestration, not provider behavior or
     real-world robustness.
12. **Prompt injection:** Insert retrieved text that says to ignore policy and reveal secrets;
   prove it stays data and cannot change allowed citations.
   - **Progressive hint:** The model double should attempt the attack so downstream validation
     is exercised.
13. **Text normalization:** Choose normalization rules for blank IDs, Unicode text, and
   blocked-fragment matching without silently changing document meaning.
   - **Progressive hint:** Normalization can close bypasses but can also merge distinct content.
14. **Numeric determinism:** Test equal and nearly equal embedding scores with a declared
   tolerance and deterministic tie-breaker.
   - **Progressive hint:** Do not rely on platform-specific incidental sort order.
15. **Token estimation:** Design a conservative preflight token estimator and explain why it
   cannot replace actual adapter accounting.
   - **Progressive hint:** Preflight should fail early on obvious excess and leave headroom.
16. **Adapter failure:** Classify embedding/model timeout and provider-like errors without
   retrying unsafe or permanent failures.
   - **Progressive hint:** Offline doubles can model exception classes and call order.
17. **Abstention:** Require abstention when no authorized evidence survives retrieval and test
   that the text model is not called.
   - **Progressive hint:** No evidence is a deterministic pre-model decision.
18. **Observability:** Design safe logs/metrics that exclude user query, context, embeddings,
   and raw model output.
   - **Progressive hint:** Use bounded stage/outcome/error-class metadata only.
19. **Metric edge cases:** Define evaluation metrics for an empty case set and zero expected
   citations without divide-by-zero ambiguity.
   - **Progressive hint:** Denominators and conventions belong in the metric contract.
20. **Regression gates:** Set deterministic pass thresholds for citation recall, abstention
   accuracy, leakage, and budgets without hiding per-case failures.
   - **Progressive hint:** Aggregate gates complement, not replace, case-level evidence.
21. **Real adapter boundary:** Design an optional hosted adapter evaluation that keeps
   credentials external and never weakens the offline default.
   - **Progressive hint:** Network, cost, and data authorization require an explicit opt-in
     gate.
22. **Threat model:** Write residual risks for retrieval poisoning, embedding inversion, model
   memorization, authorization drift, and evaluator blind spots.
   - **Progressive hint:** Controls reduce specific risks; they do not make a universal safety
     claim.

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

## Next step

Complete the
[learner file](../lessons/bridge_ai_01_application_engineering.py) and your own
adversarial cases before reviewing the
[reference implementation](../solutions/bridge_ai_01_application_engineering_solution.py)
and [solution reasoning](../solutions/bridge_ai_01_application_engineering_solutions.md).
Then apply the same boundary-first design to a local document set whose
classification and license are known.

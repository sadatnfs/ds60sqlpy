"""BRIDGE-AI-01: offline AI application engineering.

Prerequisites: Python Day 15, Bridge Day 5, and Bridge Day 8.
This answer-free learner file uses only local deterministic doubles.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

LESSON_ID = "bridge-ai-01"
PREREQUISITES = ("python-15", "bridge-05", "bridge-08")
LEVEL = "advanced"


@dataclass(frozen=True)
class Document:
    document_id: str
    text: str
    audiences: frozenset[str]
    sensitive: bool = False


@dataclass(frozen=True)
class SearchHit:
    document_id: str
    excerpt: str
    score: float


class EmbeddingModel(Protocol):
    def embed(self, text: str) -> Sequence[float]: ...


@dataclass(frozen=True)
class RetrievalPolicy:
    allowed_audiences: frozenset[str]
    top_k: int = 3
    max_context_characters: int = 1_500


@dataclass(frozen=True)
class ModelRequest:
    system_prompt: str
    query: str
    context: tuple[SearchHit, ...]
    max_output_tokens: int
    estimated_input_tokens: int


@dataclass(frozen=True)
class ModelResponse:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class TextModel(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse: ...


@dataclass(frozen=True)
class Budget:
    max_input_tokens: int = 600
    max_output_tokens: int = 120
    max_latency_ms: float = 250
    max_cost_units: int = 1_000


@dataclass(frozen=True)
class StructuredAnswer:
    answer: str
    citations: tuple[str, ...]
    abstained: bool


@dataclass(frozen=True)
class AssistantRun:
    answer: StructuredAnswer
    retrieved_ids: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    cost_units: int
    latency_ms: float


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    query: str
    expected_citations: frozenset[str]
    should_abstain: bool
    forbidden_output_fragments: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationMetrics:
    case_count: int
    citation_recall: float
    abstention_accuracy: float
    leakage_rate: float
    budget_pass_rate: float


def retrieve(
    query: str,
    documents: Sequence[Document],
    embedding_model: EmbeddingModel,
    policy: RetrievalPolicy,
) -> tuple[SearchHit, ...]:
    """Core implementation: filter access first, then rank and bound local evidence."""

    raise NotImplementedError("exclude sensitive/instructional data before embedding")


def build_request(
    query: str,
    hits: Sequence[SearchHit],
    budget: Budget,
) -> ModelRequest:
    """Core implementation: mark retrieved text as untrusted data and enforce preflight size."""

    raise NotImplementedError("serialize bounded context without promoting its instructions")


def parse_structured_answer(
    raw_text: str,
    *,
    allowed_citations: frozenset[str],
) -> StructuredAnswer:
    """Core implementation: validate exact JSON fields, types, and citation ownership."""

    raise NotImplementedError("reject malformed, extra, or unauthorized output")


def run_assistant(
    query: str,
    documents: Sequence[Document],
    *,
    embedding_model: EmbeddingModel,
    text_model: TextModel,
    retrieval_policy: RetrievalPolicy,
    budget: Budget,
    blocked_output_fragments: Sequence[str] = (),
) -> AssistantRun:
    """Core implementation: compose retrieval, validation, leakage checks, and budgets."""

    raise NotImplementedError("fail closed when evidence, schema, or budget checks fail")


def evaluate(
    cases: Sequence[EvaluationCase],
    runner: Callable[[str], AssistantRun],
    *,
    budget: Budget,
) -> EvaluationMetrics:
    """Core implementation: score citations, abstention, leakage, and budget compliance."""

    raise NotImplementedError("evaluate a checked-in deterministic dataset")


# Exercises (answer-free)
# Focus: Build an offline, deterministic retrieval-and-generation boundary with
#    authorization-before-embedding, untrusted context, exact output schemas, budgets, leakage
#    checks, and evaluation.
# Assumptions: Documents, embedding/model adapters, and evaluation cases are local deterministic
#    doubles; no API key, hosted service, or network call is required.
# Failure to watch for: Retrieving unauthorized text, trusting model-shaped JSON, or reporting a
#    passing toy evaluation as production safety evidence creates false assurance.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Validation] Validate every dataclass invariant for IDs, text, audiences, bounds,
#    token/cost budgets, and latency.
#    Hint: Fail at construction so invalid state cannot cross later boundaries.
#    Verify: Parameterize every dataclass with blank IDs/text, empty audiences, non-positive
#    bounds, non-finite scores/latency, and inconsistent budgets; assert exact construction
#    failures and one fully valid object per type.
# 2. [Math] Implement cosine similarity with mismatched-dimension and zero-vector handling.
#    Hint: Validate shape and norms before division.
#    Verify: Assert identical vectors score `1.0`, orthogonal vectors `0.0`, mismatched/empty
#    dimensions and zero norms raise `ValueError`, and near-equal comparisons use the declared
#    tolerance.
# 3. [Authorization testing] Use a recording embedding double to prove sensitive, unauthorized,
#    and quarantined documents are filtered before embedding.
#    Hint: Call history is the evidence that prohibited text never crossed the adapter.
#    Verify: Record embedding inputs for a mixed document set; assert the query and only
#    authorized, non-sensitive, non-quarantined documents are embedded and forbidden text/IDs
#    never cross the call boundary.
# 4. [Ranking] Rank equal-score documents deterministically while enforcing top-k and total
#    context-character bounds.
#    Hint: Use a stable document ID tie-breaker and apply the character budget without splitting
#    trust rules.
#    Verify: Give equal-score documents in reversed input order; assert ranking uses ascending
#    document ID, returns at most `top_k`, and total selected excerpt characters never exceed
#    the policy limit.
# 5. [Prompt boundary] Serialize context as untrusted JSON containing only approved document IDs
#    and bounded excerpts.
#    Hint: Separate system instructions, user query, and retrieved data structurally.
#    Verify: Parse each serialized context line as JSON; assert exact approved ID/text fields
#    plus the `untrusted_document_data` label, deterministic order, bounded excerpts, and no
#    unauthorized field.
# 6. [Schema validation] Implement exact structured-answer validation and test all malformed,
#    extra-field, wrong-type, duplicate-citation, and inconsistent-abstention cases.
#    Hint: Parsing JSON is only the first step; validate exact shape and semantics.
#    Verify: Parameterize missing/extra fields, wrong types, duplicate/unknown citations, and
#    inconsistent abstention; assert all raise `UnsafeModelOutput` while one exact valid object
#    is accepted unchanged.
# 7. [Adversarial testing] Use a malicious model double that cites an unretrieved document and
#    prove validation rejects it.
#    Hint: Citations are authorization claims and must be a subset of retrieved evidence.
#    Verify: Return a citation ID absent from retrieved hits; assert parsing/orchestration
#    raises `UnsafeModelOutput`, produces no accepted answer, and records the invalid model call
#    once.
# 8. [Leakage] Return a blocked private marker from the model and prove the output boundary
#    fails closed without logging the answer.
#    Hint: Leakage inspection occurs after parsing but before return/logging.
#    Verify: Return a configured private marker; assert the run fails closed, the marker is
#    absent from logs and returned objects, and only a bounded error class/outcome is
#    observable.
# 9. [Budgets] Test preflight input, actual input, output, cost-unit, and latency budget
#    failures separately.
#    Hint: Each limit is independent evidence and needs its own failure case.
#    Verify: Trigger estimated-input, reported-input, output, cost-unit, and latency limits one
#    at a time; assert each raises `BudgetExceeded` at its named gate and unaffected limits
#    still pass.
# 10. [Evaluation] Add deterministic grounded, abstention, injection-document, and
#    unauthorized-private-document cases.
#    Hint: Expected citations and forbidden fragments make safety assertions inspectable.
#    Verify: Run grounded, abstention, injection-document, and unauthorized-private cases;
#    compare exact citations/abstention, zero forbidden fragments, expected adapter calls, and
#    per-case budget outcome.
# 11. [Evidence limits] Explain which safety claims deterministic doubles prove and which
#    require a separately authorized real-adapter evaluation.
#    Hint: A controlled harness proves orchestration, not provider behavior or real-world
#    robustness.
#    Verify: Provide a two-column claim table: deterministic doubles prove orchestration/call
#    order/schema gates; provider reliability, real model quality, billing, privacy policy, and
#    adversarial robustness remain unproved.
# 12. [Prompt injection] Insert retrieved text that says to ignore policy and reveal secrets;
#    prove it stays data and cannot change allowed citations.
#    Hint: The model double should attempt the attack so downstream validation is exercised.
#    Verify: Insert an instruction-attack document and configure the model to follow it if seen;
#    assert the document is quarantined or serialized only as data and allowed citations/output
#    policy cannot expand.
# 13. [Text normalization] Choose normalization rules for blank IDs, Unicode text, and
#    blocked-fragment matching without silently changing document meaning.
#    Hint: Normalization can close bypasses but can also merge distinct content.
#    Verify: Test whitespace-only IDs, composed/decomposed Unicode, and case/normalization
#    variants of blocked markers; document which normalize to equality and which remain distinct
#    without altering source meaning.
# 14. [Numeric determinism] Test equal and nearly equal embedding scores with a declared
#    tolerance and deterministic tie-breaker.
#    Hint: Do not rely on platform-specific incidental sort order.
#    Verify: Rank equal and epsilon-different scores under the declared tolerance; assert
#    deterministic ID tie-breaking and identical order across repeated runs.
# 15. [Token estimation] Design a conservative preflight token estimator and explain why it
#    cannot replace actual adapter accounting.
#    Hint: Preflight should fail early on obvious excess and leave headroom.
#    Verify: For representative strings, record the conservative estimated token count and
#    headroom; assert obvious oversize input fails preflight and actual adapter usage remains
#    the authoritative post-call value.
# 16. [Adapter failure] Classify embedding/model timeout and provider-like errors without
#    retrying unsafe or permanent failures.
#    Hint: Offline doubles can model exception classes and call order.
#    Verify: Configure timeout/transient/permanent/unsafe-output exceptions; assert only the
#    explicitly retryable adapter class is retried within its bound and permanent or unsafe
#    failures have one call.
# 17. [Abstention] Require abstention when no authorized evidence survives retrieval and test
#    that the text model is not called.
#    Hint: No evidence is a deterministic pre-model decision.
#    Verify: Use a query with no authorized hit; assert an abstaining `AssistantRun` is returned
#    (or the declared abstention path), citations are empty, and text-model call count is zero.
# 18. [Observability] Design safe logs/metrics that exclude user query, context, embeddings, and
#    raw model output.
#    Hint: Use bounded stage/outcome/error-class metadata only.
#    Verify: Capture logs and metrics for pass/failure; assert only bounded
#    stage/outcome/error-class/count fields appear and query, context, embeddings, raw output,
#    document IDs, and credentials are absent.
# 19. [Metric edge cases] Define evaluation metrics for an empty case set and zero expected
#    citations without divide-by-zero ambiguity.
#    Hint: Denominators and conventions belong in the metric contract.
#    Verify: Evaluate an empty case set and a case with zero expected citations; assert
#    documented finite metric values with no division error or NaN and retain the denominator in
#    results.
# 20. [Regression gates] Set deterministic pass thresholds for citation recall, abstention
#    accuracy, leakage, and budgets without hiding per-case failures.
#    Hint: Aggregate gates complement, not replace, case-level evidence.
#    Verify: Apply explicit citation-recall, abstention, leakage-zero, and budget thresholds;
#    assert one failing case remains visible even if aggregate averages would otherwise pass.
# 21. [Real adapter boundary] Design an optional hosted adapter evaluation that keeps
#    credentials external and never weakens the offline default.
#    Hint: Network, cost, and data authorization require an explicit opt-in gate.
#    Verify: Specify an opt-in environment flag, external credential source, bounded
#    dataset/cost/time, adapter version record, and cleanup; assert the normal test command
#    cannot import/call the hosted adapter.
# 22. [Threat model] Write residual risks for retrieval poisoning, embedding inversion, model
#    memorization, authorization drift, and evaluator blind spots.
#    Hint: Controls reduce specific risks; they do not make a universal safety claim.
#    Verify: Produce residual-risk rows for retrieval poisoning, embedding inversion,
#    memorization, authorization drift, and evaluator blind spots, each with owner, current
#    control, detection evidence, and next action.


def main() -> int:
    print("BRIDGE-AI-01 starter loaded; no network, API key, or hosted model is used.")
    print("Implement access filtering and deterministic doubles before orchestration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

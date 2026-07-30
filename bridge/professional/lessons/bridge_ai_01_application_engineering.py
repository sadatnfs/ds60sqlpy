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
# 2. [Math] Implement cosine similarity with mismatched-dimension and zero-vector handling.
#    Hint: Validate shape and norms before division.
# 3. [Authorization testing] Use a recording embedding double to prove sensitive, unauthorized,
#    and quarantined documents are filtered before embedding.
#    Hint: Call history is the evidence that prohibited text never crossed the adapter.
# 4. [Ranking] Rank equal-score documents deterministically while enforcing top-k and total
#    context-character bounds.
#    Hint: Use a stable document ID tie-breaker and apply the character budget without splitting
#    trust rules.
# 5. [Prompt boundary] Serialize context as untrusted JSON containing only approved document IDs
#    and bounded excerpts.
#    Hint: Separate system instructions, user query, and retrieved data structurally.
# 6. [Schema validation] Implement exact structured-answer validation and test all malformed,
#    extra-field, wrong-type, duplicate-citation, and inconsistent-abstention cases.
#    Hint: Parsing JSON is only the first step; validate exact shape and semantics.
# 7. [Adversarial testing] Use a malicious model double that cites an unretrieved document and
#    prove validation rejects it.
#    Hint: Citations are authorization claims and must be a subset of retrieved evidence.
# 8. [Leakage] Return a blocked private marker from the model and prove the output boundary
#    fails closed without logging the answer.
#    Hint: Leakage inspection occurs after parsing but before return/logging.
# 9. [Budgets] Test preflight input, actual input, output, cost-unit, and latency budget
#    failures separately.
#    Hint: Each limit is independent evidence and needs its own failure case.
# 10. [Evaluation] Add deterministic grounded, abstention, injection-document, and
#    unauthorized-private-document cases.
#    Hint: Expected citations and forbidden fragments make safety assertions inspectable.
# 11. [Evidence limits] Explain which safety claims deterministic doubles prove and which
#    require a separately authorized real-adapter evaluation.
#    Hint: A controlled harness proves orchestration, not provider behavior or real-world
#    robustness.
# 12. [Prompt injection] Insert retrieved text that says to ignore policy and reveal secrets;
#    prove it stays data and cannot change allowed citations.
#    Hint: The model double should attempt the attack so downstream validation is exercised.
# 13. [Text normalization] Choose normalization rules for blank IDs, Unicode text, and
#    blocked-fragment matching without silently changing document meaning.
#    Hint: Normalization can close bypasses but can also merge distinct content.
# 14. [Numeric determinism] Test equal and nearly equal embedding scores with a declared
#    tolerance and deterministic tie-breaker.
#    Hint: Do not rely on platform-specific incidental sort order.
# 15. [Token estimation] Design a conservative preflight token estimator and explain why it
#    cannot replace actual adapter accounting.
#    Hint: Preflight should fail early on obvious excess and leave headroom.
# 16. [Adapter failure] Classify embedding/model timeout and provider-like errors without
#    retrying unsafe or permanent failures.
#    Hint: Offline doubles can model exception classes and call order.
# 17. [Abstention] Require abstention when no authorized evidence survives retrieval and test
#    that the text model is not called.
#    Hint: No evidence is a deterministic pre-model decision.
# 18. [Observability] Design safe logs/metrics that exclude user query, context, embeddings, and
#    raw model output.
#    Hint: Use bounded stage/outcome/error-class metadata only.
# 19. [Metric edge cases] Define evaluation metrics for an empty case set and zero expected
#    citations without divide-by-zero ambiguity.
#    Hint: Denominators and conventions belong in the metric contract.
# 20. [Regression gates] Set deterministic pass thresholds for citation recall, abstention
#    accuracy, leakage, and budgets without hiding per-case failures.
#    Hint: Aggregate gates complement, not replace, case-level evidence.
# 21. [Real adapter boundary] Design an optional hosted adapter evaluation that keeps
#    credentials external and never weakens the offline default.
#    Hint: Network, cost, and data authorization require an explicit opt-in gate.
# 22. [Threat model] Write residual risks for retrieval poisoning, embedding inversion, model
#    memorization, authorization drift, and evaluator blind spots.
#    Hint: Controls reduce specific risks; they do not make a universal safety claim.


def main() -> int:
    print("BRIDGE-AI-01 starter loaded; no network, API key, or hosted model is used.")
    print("Implement access filtering and deterministic doubles before orchestration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

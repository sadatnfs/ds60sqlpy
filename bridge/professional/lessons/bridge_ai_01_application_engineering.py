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
    """Exercise 1: filter access first, then rank and bound local evidence."""

    raise NotImplementedError("exclude sensitive/instructional data before embedding")


def build_request(
    query: str,
    hits: Sequence[SearchHit],
    budget: Budget,
) -> ModelRequest:
    """Exercise 2: mark retrieved text as untrusted data and enforce preflight size."""

    raise NotImplementedError("serialize bounded context without promoting its instructions")


def parse_structured_answer(
    raw_text: str,
    *,
    allowed_citations: frozenset[str],
) -> StructuredAnswer:
    """Exercise 3: validate exact JSON fields, types, and citation ownership."""

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
    """Exercise 4: compose retrieval, validation, leakage checks, and budgets."""

    raise NotImplementedError("fail closed when evidence, schema, or budget checks fail")


def evaluate(
    cases: Sequence[EvaluationCase],
    runner: Callable[[str], AssistantRun],
    *,
    budget: Budget,
) -> EvaluationMetrics:
    """Exercise 5: score citations, abstention, leakage, and budget compliance."""

    raise NotImplementedError("evaluate a checked-in deterministic dataset")


def main() -> int:
    print("BRIDGE-AI-01 starter loaded; no network, API key, or hosted model is used.")
    print("Implement access filtering and deterministic doubles before orchestration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

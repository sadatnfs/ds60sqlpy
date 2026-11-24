"""Learner-facing plan outcomes: one observable action sentence per lesson.

The classroom lesson header shows these sentences, so each names work the
learner can be seen to do in that lesson's exercises rather than defining the
topic. The renderer copies them into ``track.json``.
"""

OUTCOMES = {
    "llm-applied-001": (
        "Route each subject-assistant request to prompting, retrieval, a deterministic tool "
        "or fine-tuning, and write a measurable task contract with a held-out family split."
    ),
    "llm-applied-002": (
        "Validate extracted data-science records against type, semantic and provenance checks, "
        "rejecting impossible counts and keeping missing values distinct from zero."
    ),
    "llm-applied-003": (
        "Build a versioned prompt artifact that keeps untrusted evidence as data, reserves "
        "response capacity within a context budget and isolates evaluation examples."
    ),
    "llm-applied-004": (
        "Build a versioned corpus manifest with source permissions and content hashes, select "
        "active versions explicitly and detect family leakage between training and test data."
    ),
    "llm-applied-005": (
        "Split documents into overlapping chunks whose start and end offsets reproduce the "
        "cited source text, and measure the duplication that overlap adds."
    ),
    "llm-applied-006": (
        "Compute BM25 scores from term frequency, inverse document frequency and length "
        "normalization, and rank a small corpus with deterministic ties."
    ),
    "llm-applied-007": (
        "Rank documents by cosine similarity between embedding vectors, reject zero or "
        "incompatible vectors, and show where geometric rank fails to establish relevance."
    ),
    "llm-applied-008": (
        "Combine lexical and dense rankings with reciprocal rank fusion, rerank a bounded "
        "candidate set and measure the candidate-recall ceiling."
    ),
    "llm-applied-009": (
        "Enforce access-scope filters before retrieval scoring so restricted documents never "
        "reach answer context, cache keys or traces."
    ),
    "llm-applied-010": (
        "Rewrite queries with a controlled synonym rule and follow linked evidence within a "
        "declared hop budget without crossing authorization boundaries."
    ),
    "llm-applied-011": (
        "Map each answer claim to a cited, version-bound evidence span, and abstain when no "
        "admitted source supports it."
    ),
    "llm-applied-012": (
        "Evaluate retrieval recall, reciprocal rank and answer support separately, and use "
        "oracle-context controls to locate where a pipeline failed."
    ),
    "llm-applied-013": (
        "Compare two assistants with paired, family-level bootstrap uncertainty, report "
        "coverage alongside answered accuracy and block severe boundary failures."
    ),
    "llm-applied-014": (
        "Construct supervised fine-tuning records with answer-only target masks, detect "
        "destructive truncation and keep example families disjoint across splits."
    ),
    "llm-applied-015": (
        "Train a tiny causal decoder with full supervised fine-tuning on masked answer "
        "targets, then evaluate a frozen held-out prompt and record an honest receipt."
    ),
    "llm-applied-016": (
        "Implement a LoRA update on a frozen linear weight, count its stored parameters, take "
        "an adapter-only gradient step and verify the merged weight."
    ),
    "llm-applied-017": (
        "Apply 4-bit quantization to a frozen base matrix, pack and dequantize its codes, train "
        "only a low-rank adapter and account for storage honestly."
    ),
    "llm-applied-018": (
        "Compare full and adapter fine-tuning from one cloned base under fixed update budgets, "
        "prove base preservation and evaluate the same frozen held-out task."
    ),
    "llm-applied-019": (
        "Compute a DPO-style preference loss and its gradient from policy and reference "
        "margins, and distinguish that offline update from a complete RLHF workflow."
    ),
    "llm-applied-020": (
        "Train a query projection with a contrastive objective and a small pairwise reranker, "
        "then check held-out scores and detect false-negative identities."
    ),
    "llm-applied-021": (
        "Inspect an optional pretrained-model recipe, tracing pinned revision, license, "
        "chat-template boundaries and trainer labels before any offline training run."
    ),
    "llm-applied-022": (
        "Dispatch only typed, bounded data-science tool requests, reject invalid values and "
        "excess work, and verify generated explanations against computed results."
    ),
    "llm-applied-023": (
        "Enforce freshness, call-budget and allowlisted-trace controls around a domain "
        "assistant, using an injected UTC clock and abstaining on stale evidence."
    ),
    "llm-applied-024": (
        "Assemble an end-to-end subject assistant that enforces access, grounds or abstains, "
        "computes results deterministically and passes a bounded acceptance evaluation."
    ),
}

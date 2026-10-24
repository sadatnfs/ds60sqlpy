from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
ROWS = [
    (
        "llm-043",
        "Encoder, decoder and encoder-decoder architectures and objectives",
        "python-core",
        [
            "architecture",
            "bidirectional encoder",
            "causal decoder",
            "cross-attention",
            "training objective",
        ],
    ),
    (
        "llm-044",
        "RoPE, relative positions, ALiBi and long-context limits",
        "python-core",
        ["RoPE", "relative positions", "ALiBi", "position offsets", "long-context extrapolation"],
    ),
    (
        "llm-045",
        "Pre/post normalization, RMSNorm and gated feed-forward networks",
        "llm-torch-cpu",
        ["pre-norm", "post-norm", "RMSNorm", "SwiGLU", "Jacobian", "parameter budget"],
    ),
    (
        "llm-046",
        "MHA, MQA, GQA and blockwise exact attention",
        "python-core",
        ["MHA", "MQA", "GQA", "KV cache", "online softmax", "FlashAttention boundaries"],
    ),
    (
        "llm-047",
        "Sparse experts, routing capacity and load balancing",
        "python-core",
        ["mixture of experts", "top-k routing", "capacity", "load balancing", "expert parallelism"],
    ),
    (
        "llm-048",
        "Exact speculative decoding and cache rollback",
        "python-core",
        [
            "speculative decoding",
            "acceptance probability",
            "residual distribution",
            "bonus token",
            "cache rollback",
        ],
    ),
]


def append_plan():
    path = ROOT / "docs/expansion/plans/llm-theory.json"
    plan = json.loads(path.read_text())
    existing = {row["id"] for row in plan["lessons"]}
    for index, (identity, title, profile, concepts) in enumerate(ROWS):
        if identity in existing:
            continue
        plan["lessons"].append(
            dict(
                id=identity,
                title=title,
                level="advanced",
                minutes=210,
                prerequisites=["llm-042" if index == 0 else ROWS[index - 1][0]],
                runtime=profile,
                outcome=f"Explain and verify {title.lower()} on bounded CPU fixtures.",
                lab="Derive exact values, implement the mechanism and test a controlled failure.",
                verification="Compare independent numerical oracles and report model/runtime limits.",
                concepts=concepts,
            )
        )
    plan["summary"] = (
        "48 detailed lessons on how language models work, from token probabilities and causal attention to Transformers, adaptation, efficient attention, expert routing and exact decoding mechanisms."
    )
    path.write_text(json.dumps(plan, indent=2) + "\n")

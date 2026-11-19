# ruff: noqa: E501
"""Authored learning objectives for llm-043 to llm-048 (outcome, lab, verification)."""

OBJECTIVES = {
    "llm-043": (
        "Distinguish encoder, decoder and encoder-decoder attention by which positions each query may read, and connect each mask to its training objective.",
        "With zero queries and keys and values [[2, 0], [0, 2], [6, 6]], compare all-allowed (encoder) and causal (decoder) attention, build shifted decoder targets and a masked-token target, then add source padding to cross-attention.",
        "Encoder rows all equal [8/3, 8/3] while decoder rows are [2, 0], [1, 1] and [8/3, 8/3]; with the third source position padded, both cross-attention outputs are [1, 1] and the padded position receives weight 0.",
    ),
    "llm-044": (
        "Apply rotary position embeddings, show that rotated dot products depend only on relative position, and compare RoPE with an ALiBi distance penalty without treating computability as long-context quality.",
        "Rotate [1, 0] by a quarter turn, test the relative dot-product identity for q = [1, 2] and k = [3, -1], compute an ALiBi row, and catch a cache that restarts positions at 0.",
        "The rotated vector is approximately [0, 1] with norm 1; the relative identity holds within 1e-12; the ALiBi row normalizes to [1/7, 2/7, 4/7]; an encoding at position 1000000 is finite while long_context_quality_verified stays False and an odd width is rejected.",
    ),
    "llm-045": (
        "Compare pre- and post-normalization residual paths, compute RMSNorm and LayerNorm by hand, and derive the gradients of a SwiGLU gate.",
        "Normalize [3, 4] with both normalizers, trace the residual Jacobians, check the RMSNorm Jacobian formula against autograd, and match feed-forward parameter budgets.",
        "RMSNorm keeps a nonzero mean while LayerNorm output has mean approximately 0; LayerNorm is invariant to a constant shift of [1, 2, 3] and RMSNorm is not; both stay finite on the zero vector; plain and gated feed-forward blocks both use 48 weights.",
    ),
    "llm-046": (
        "Separate attention architecture (how many key-value heads) from attention execution (dense or blockwise online softmax), and count the cache and projection memory each design needs.",
        "Use batch 1, time 5 and 4 query heads of width 2 in float32, compare 4, 2 and 1 key-value heads, then check blockwise online attention against dense attention at extreme scores and several block sizes.",
        "Raw KV cache bytes are 320, 160 and 80 and projection weights 256, 192 and 160 for model width 8 without biases; online and dense outputs agree within 1e-12; 3 KV heads for 4 query heads and an all-false attention row both raise ValueError.",
    ),
    "llm-047": (
        "Route tokens to sparse experts with top-k gating, enforce expert capacity with a residual fallback, and compute the load-balancing loss and the active parameter count.",
        "Mix experts I, 2I and -I with selected router probabilities 3/4 and 1/4, then route four tokens under capacity 2 and compute the auxiliary loss.",
        "Outputs are [1.25, 0], [0, 1.75] and [-0.25, -0.25]; capacity 2 accepts 2 and 1 tokens and the overflow token keeps its input; the auxiliary loss is 0.012; top-k 0 and capacity 0 raise ValueError and a top-2 tie selects indices 0 and 1.",
    ),
    "llm-048": (
        "Implement exact speculative decoding: accept a draft token with probability min(1, p/q), resample a rejection from the normalized residual, and roll the cache back to the committed prefix.",
        "With target p = [0.5, 0.3, 0.2] and draft q = [0.2, 0.5, 0.3], compute the accepted mass, rejection mass and residual, then run accepted, rejected and all-accepted rounds and roll back real K/V arrays.",
        "Accepted mass [0.2, 0.3, 0.2], rejection mass 0.3 and residual [1, 0, 0] recombine to p; the rolled-back cache matches a fresh cache built from [2, 0, 0]; with p = q the rejection mass is 0, an accepted EOS stops generation, the token cap holds and unsupported proposals raise ValueError.",
    ),
}

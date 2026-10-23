"""llm-applied-008: Hybrid retrieval, reciprocal-rank fusion and reranking.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fuse two rankings
# Fuse lexical[a, b, c] and dense[b, d, a] with constant60.
# Expected: b ranks first, a second.

# Exercise 2: Inspect one exact contribution
# Calculate the fused score ofb as1/62+1/61.
# Expected: computed b score equals that sum within1e-12.

# Exercise 3: Prevent duplicate votes
# Repeatb inside one ranking and compare with its deduplicated form.
# Expected: fusion result unchanged.

# Exercise 4: Rerank a bounded candidate set
# Use candidatesa, b, c with authored relevance features0, 2, 1 and sort descending
# feature then ID.
# Expected: orderb, c, a.

# Exercise 5: Expose a candidate-recall ceiling
# Declare relevant documentd but supply only candidatesa, b, c.
# Expected: candidate recall0 and reranker cannot return d.

# Exercise 6: Reject invalid fusion policy
# Use constant0 or a repeated non-string identifier and apply the declared validation.
# Expected: ValueError for nonpositive constant; TypeError for non-string ID.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

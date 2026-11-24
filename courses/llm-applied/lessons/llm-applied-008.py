"""llm-applied-008: Hybrid retrieval, reciprocal-rank fusion and reranking.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fuse two rankings
# Fuse lexical [a, b, c] and dense [b, d, a] with constant 60.
# Expected: b ranks first, a second.

# Exercise 2: Inspect one exact contribution
# Calculate the fused score of b as 1/62+1/61.
# Expected: computed b score equals that sum within 1e-12.

# Exercise 3: Prevent duplicate votes
# Repeat b inside one ranking and compare with its deduplicated form.
# Expected: fusion result unchanged.

# Exercise 4: Rerank a bounded candidate set
# Use candidates a, b, c with authored relevance features 0, 2, 1 and sort descending
# feature then ID.
# Expected: order b, c, a.

# Exercise 5: Expose a candidate-recall ceiling
# Declare relevant document d but supply only candidates a, b, c.
# Expected: candidate recall 0 and reranker cannot return d.

# Exercise 6: Reject invalid fusion policy
# Use constant 0 or a repeated non-string identifier and apply the declared validation.
# Expected: ValueError for nonpositive constant; TypeError for non-string ID.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

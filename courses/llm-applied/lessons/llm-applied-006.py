"""llm-applied-006: Lexical retrieval and BM25 from first principles.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Rank a discriminating term
# Rank documents a=account randomization, b=visit counts and c=account outcomes for the
# query randomization.
# Expected: a ranks first with a positive score; the other scores are0.

# Exercise 2: Inspect term rarity
# Compare IDF for a term present in1 of 3 documents with a term present in2 of 3.
# Expected: the rarer term has larger IDF.

# Exercise 3: Verify saturation
# Disable length normalization with b=0 and compare term frequencies1, 2, 10 under the
# same IDF.
# Expected: scores increase, but10 occurrences yield less than10 times the single-occurrence score.

# Exercise 4: Expose a synonym miss
# Query purchase against a document containing only buy.
# Expected: score0 despite the semantic relationship.

# Exercise 5: Make ties deterministic
# Query an absent word with document IDs z, a, b.
# Expected: order a, b, z with zero scores.

# Exercise 6: Check corpus edge cases
# Score an empty corpus and a corpus containing one empty document.
# Expected: empty result for no documents; finite zero score for an empty document.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

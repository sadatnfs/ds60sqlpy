"""llm-applied-007: Embedding retrieval, similarity and representation limits.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Rank fixed topic vectors
# Use query[1, 0, 0] and documents purchase[1, .1, 0], geometry[0, 1, 0], mixed[.5, .5,
# 0].
# Expected: purchase ranks first, mixed second, geometry last.

# Exercise 2: Separate cosine from magnitude
# Scale the purchase vector by 10 and compare its cosine score with the original.
# Expected: cosine unchanged within1e-12; raw dot product multiplies by 10.

# Exercise 3: Expose hand-authored synonym knowledge
# Assign buy the same literal vector as purchase and compare retrieval with an exact-token
# overlap baseline.
# Expected: vector scores match; literal word overlap is empty.

# Exercise 4: Reject zero and nonfinite vectors
# Normalize[0, 0] and[1, NaN] through the checked helper.
# Expected: both raise ValueError.

# Exercise 5: Reject incompatible spaces
# Compare query metadata modelA with an index encoded by modelB, even when both have
# width3.
# Expected: space identity mismatch blocks retrieval.

# Exercise 6: Measure a domain failure
# Give an irrelevant document a high-scoring vector and record that geometric rank does
# not establish relevance.
# Expected: top-ranked IDwrong is outside the authored relevant set.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

"""llm-036: Retrieval: what RAG changes and what it cannot supply.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Rank a different query
# Query has sides against the same six documents with token overlap and ID tie-breaks;
# return the top 3.
# Expected: top 3 IDs d1, d4, d5: two tied overlaps ordered by ID, then the single overlap.

# Exercise 2: Measure recall with a tie-filled slot
# Use relevant IDs d3 and d4 for the query round circle and compute recall at 1 and 2.
# Expected: ranking d3, d1; recall 0.5 at both 1 and 2.

# Exercise 3: Handle missing evidence
# Ask the orbital period of a comet absent from the corpus and require evidence before
# answering.
# Expected: abstain; relevant set empty.

# Exercise 4: Treat retrieved instructions as data
# Retrieve the command-like document for query command and retain it as a string only.
# Expected: document d6 returned; no action executed.

# Exercise 5: Keep deterministic ties
# Query an absent word so all lexical scores tie, then compare the first three IDs.
# Expected: d1, d2, d3 under ID ordering.

# Exercise 6: Separate retrieval and truth
# Record a retrieved relevant snippet but an answer with an unsupported extra claim.
# Expected: retrieval pass True; answer support False.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

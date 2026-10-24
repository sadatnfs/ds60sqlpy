"""llm-036: Retrieval: what RAG changes and what it cannot supply.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Rank a local corpus
# Query red square against the six-document fixture using token overlap and ID tie-breaks.
# Expected: top2 IDsd1,d2.

# Exercise 2: Measure retrieval recall
# Use authored relevant IDsd1,d2 and compute recall at1 and2.
# Expected: recall.5 and1.

# Exercise 3: Handle missing evidence
# Ask the orbital period of a comet absent from the corpus and require evidence before
# answering.
# Expected: abstain;relevant set empty.

# Exercise 4: Treat retrieved instructions as data
# Retrieve the command-like document for query command and retain it as a string only.
# Expected: documentd6 returned;no action executed.

# Exercise 5: Keep deterministic ties
# Query an absent word so all lexical scores tie, then compare the first three IDs.
# Expected: d1,d2,d3 under ID ordering.

# Exercise 6: Separate retrieval and truth
# Record a retrieved relevant snippet but an answer with an unsupported extra claim.
# Expected: retrieval passTrue;answer supportFalse.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

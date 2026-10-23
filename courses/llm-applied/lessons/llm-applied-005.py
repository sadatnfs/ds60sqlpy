"""llm-applied-005: Chunking, overlap, offsets and context budgets.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Split a fixed document
# Chunk one two three four five six seven with size 3 and overlap 1.
# Expected: chunks one two three, three four five and five six seven.

# Exercise 2: Verify citation offsets
# For every chunk, slice the original text using its start and end offsets.
# Expected: every source slice equals the stored chunk text.

# Exercise 3: Preserve unusual whitespace
# Chunk alpha, two spaces, beta, a newline and gamma with size 2 and overlap 0.
# Expected: first chunk retains the double space; second chunk is gamma.

# Exercise 4: Measure overlap duplication
# Count total stored chunk token occurrences versus original source token positions in the
# first fixture.
# Expected: 9 stored token occurrences versus7 source positions.

# Exercise 5: Reject invalid policies
# Try overlap equal to window size, negative overlap and size 0.
# Expected: all policies raise ValueError before iteration.

# Exercise 6: Handle empty and short sources
# Chunk empty text and a two-token string with size 5.
# Expected: empty list for empty text; one short chunk for the two-token source.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

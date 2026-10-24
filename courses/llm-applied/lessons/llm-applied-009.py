"""llm-applied-009: Metadata filtering and access-controlled retrieval.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Filter before scoring
# Give a public-only request the six-document corpus and inspect admitted IDs.
# Expected: private-v1 absent before ranking.

# Exercise 2: Permit an explicitly privileged scope
# Use allowed scopespublic, restricted and compare the admitted set.
# Expected: all6 documents admitted.

# Exercise 3: Partition answer caches
# Build cache keys for the same question under public-only and privileged scope sets.
# Expected: keys differ.

# Exercise 4: Invalidate on corpus change
# Change corpus-v1 tocorpus-v2 under the same access policy.
# Expected: cache key changes.

# Exercise 5: Keep hostile evidence inert
# Inspectattack-v1 while retaining a public-only policy.
# Expected: scope set remains exactlypublic; private-v1 still excluded.

# Exercise 6: Avoid restricted identifiers in public traces
# Create a trace from admitted result IDs only and check it contains no restricted ID.
# Expected: trace contains only public document IDs.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

"""llm-applied-010: Query rewriting and bounded multi-hop retrieval.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Apply a controlled synonym rewrite
# Rewritebuy rate usingbuy->purchase while preserving the original question.
# Expected: rewrittenpurchase rate; original unchanged.

# Exercise 2: Retain a rewrite trace
# Record the original, rewritten query and policy version.
# Expected: trace includes all three fields.

# Exercise 3: Follow two evidence hops
# Use graphmetric->exclusions->test_accounts with a two-hop bound.
# Expected: visitedmetric, exclusions, test_accounts.

# Exercise 4: Stop at the declared depth
# Run the same graph with a one-hop bound, then reject fractional, Boolean, NaN and
# negative budgets.
# Expected: test_accounts is absent; invalid budgets raise ValueError before traversal.

# Exercise 5: Break a retrieval cycle
# Addtest_accounts->metric and traverse with a larger bound.
# Expected: each document appears once.

# Exercise 6: Preserve authorization across hops
# Remove a restricted target from the admitted graph and ensure links to it are not
# followed.
# Expected: restricted document never appears.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

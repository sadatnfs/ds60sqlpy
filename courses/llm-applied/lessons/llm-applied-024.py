"""llm-applied-024: Capstone: a grounded and evaluated data-science subject assistant.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Answer a supported domain definition
# Ask the public assistant for conversion_definition.
# Expected: answered with metric-v1 citation and source text.

# Exercise 2: Abstain on missing evidence
# Ask for comet_period, which has no supporting corpus entry.
# Expected: unknown with missing evidence reason.

# Exercise 3: Enforce access before answering
# Ask a public-only assistant for restricted_threshold, then ask a separately authorized
# assistant.
# Expected: public unknown; authorized answer cites private-v1.

# Exercise 4: Compute a data-science result deterministically
# Calculate 3 purchases over 10 eligible visits and reject 11 purchases over 10 visits.
# Expected: rate 0.3; invalid counts raise ValueError.

# Exercise 5: Evaluate fixed task and boundary cases
# Score supported, missing and restricted-public questions against their expected statuses.
# Expected: 3 of 3 status contracts pass; citation integrity checked separately.

# Exercise 6: Issue a bounded capstone decision
# Record local fixture acceptance while leaving pretrained generation, real identity
# integration and production readiness unverified.
# Expected: local_fixture_pass True; production_go no-go.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

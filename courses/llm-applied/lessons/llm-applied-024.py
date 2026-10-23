"""llm-applied-024: Capstone: a grounded and evaluated data-science subject assistant.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Answer a supported domain definition
# Ask the public assistant forconversion_definition.
# Expected: answered withmetric-v1 citation and source text.

# Exercise 2: Abstain on missing evidence
# Ask forcomet_period, which has no supporting corpus entry.
# Expected: unknown withmissing evidence reason.

# Exercise 3: Enforce access before answering
# Ask a public-only assistant forrestricted_threshold, then ask a separately authorized
# assistant.
# Expected: publicunknown; authorizedanswercitesprivate-v1.

# Exercise 4: Compute a data-science result deterministically
# Calculate3 purchases over10 eligible visits and reject11 purchases over10 visits.
# Expected: rate.3; invalid counts raiseValueError.

# Exercise 5: Evaluate fixed task and boundary cases
# Score supported, missing andrestricted-public questions against their expected statuses.
# Expected: 3 of 3 status contracts pass; citation integrity checked separately.

# Exercise 6: Issue a bounded capstone decision
# Record local fixture acceptance while leaving pretrained generation, realidentity
# integration andproduction readiness unverified.
# Expected: local_fixture_passTrue; production_gono-go.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

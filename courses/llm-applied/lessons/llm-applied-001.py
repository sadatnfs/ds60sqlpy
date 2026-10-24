"""llm-applied-001: The subject assistant decision: prompts, retrieval or fine-tuning.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Route a changing definition
# Describe a request for the current conversion-rate definition requiring a citation.
# Expected: route retrieval; reason current cited evidence.

# Exercise 2: Route an exact calculation
# Describe a request to sum validated purchase amounts and return an integer-cent total.
# Expected: route deterministic_tool; reason exact computation.

# Exercise 3: Require evidence before fine-tuning
# Describe a stable schema-formatting gap with zero governed examples, then with 120
# reviewed examples.
# Expected: first measure_baseline; then adaptation_candidate.

# Exercise 4: Keep mechanisms composable
# A task needs current policy citations and a stable response schema; state which stage
# retrieves evidence and which might be adapted.
# Expected: retrieval remains required; format adaptation is separate.

# Exercise 5: Avoid training on secrets as an access mechanism
# Mark restricted facts as requiring an access policy and reject the idea that a fine-
# tuned model enforces per-user authorization.
# Expected: authorization remains an external gate.

# Exercise 6: Write a measurable subject-assistant contract
# Define an assistant for study-design extraction with fields assignment_unit, outcome and
# unknown status; name a held-out family split.
# Expected: contract has exact fields, an abstention policy and a family split.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

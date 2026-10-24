"""llm-applied-011: Grounded claims, citations and evidence-based abstention.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Return a supported extractive answer
# Answer the conversion-definition question from the metric document and its first
# sentence.
# Expected: statusanswered; one claim; citation slices the exact sentence.

# Exercise 2: Reject a corrupted span
# Change the stored quote while leaving citation offsets unchanged.
# Expected: citation integrity check returnsFalse.

# Exercise 3: Abstain on missing evidence
# Request an unsupported comet-period answer with no admitted supporting document.
# Expected: statusunknown; claims empty; reasonmissing evidence.

# Exercise 4: Separate a valid citation from support
# Cite the metric document for a claim about statistical significance and inspect the
# authored support map.
# Expected: document exists but significance claim unsupported.

# Exercise 5: Bind the source version
# Compare a citation requiringversion1 with a suppliedversion2 document.
# Expected: version mismatch blocks citation reuse.

# Exercise 6: Keep arithmetic separate from prose
# Compute3 purchases over10 visits and attach the deterministic result to an explanation
# record.
# Expected: rate.3 with input counts preserved.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

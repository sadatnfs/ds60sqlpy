"""llm-applied-004: Corpus provenance, versions and evaluation isolation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fingerprint authored sources
# Add source=course-authored, permission=course-fixture and SHA256 to each local document.
# Expected: 6 complete records; all hashes contain64 characters.

# Exercise 2: Detect a changed definition
# Create metric-v2 with changed text and compare content hashes to metric-v1.
# Expected: hash differs; family remains metric; version is2.

# Exercise 3: Choose an active version explicitly
# Select the highest version per family from metric-v1, metric-v2 and trial-v1.
# Expected: active IDs metric-v2 and trial-v1.

# Exercise 4: Detect family leakage
# Place metric-v1 in training and metric-v2 in testing, then compare their families.
# Expected: family intersection contains metric despite different hashes.

# Exercise 5: Refuse incomplete admission metadata
# Remove permission from one record and validate admission.
# Expected: ValueError for missing permission.

# Exercise 6: Keep instruction-like documents inert
# Inspect attack-v1 and confirm its text does not alter the manifest validator or access
# metadata.
# Expected: attack text remains data; restricted record remains restricted.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")

"""llm-006: predict from the companion guide, then modify an owned copy."""

import unicodedata

texts = ["cat", "café", "🙂"]
counts = [(len(text), len(text.encode("utf-8"))) for text in texts]
assert counts == [(3, 3), (4, 5), (1, 4)]
assert all(text.encode("utf-8").decode("utf-8") == text for text in texts)
print(counts)


composed = "é"
# Construct directly to avoid a platform-dependent source-file normalization step.
decomposed = "e" + chr(0x0301)
assert composed != decomposed
assert composed.encode("utf-8") != decomposed.encode("utf-8")
assert unicodedata.normalize("NFC", decomposed) == composed
print(len(composed), len(decomposed))

# Exercise 1: Trace the encoding units
# Calculate code-point and UTF-8 byte counts for cat, café and 🙂 before running the
# example.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a strict round trip
# Implement encode_record(text,policy) with none/NFC policies and a matching strict
# decoder.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Diagnose canonical duplicates
# Compare é and e+combining-accent under raw and NFC identity.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Reject malformed UTF-8
# Strictly decode byte 0xff, then compare an explicit errors=replace diagnostic.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Handle empty and unknown policies
# Round-trip the empty string and request policy mystery.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Choose identity before splitting
# Use documents café, cafe+combining-accent and tea. Compare raw versus NFC distinct
# counts before assigning source families.
# Add your attempt and keep its observed values or exception beside your prediction.

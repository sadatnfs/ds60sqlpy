"""nlp-004 learner workspace. This is a toy word-BPE investigation."""
import re

text = "can't pay."
print(text.split())
print(re.findall(r"\w+|[^\w\s]", text))
words = {"low": 3, "lower": 1}

# Exercise 1: Compare the three segmentation policies and retain source spans.
# Expected: the guide's three token lists; pay occupies[6,9).
# Exercise 2: Count adjacent pairs using word frequencies.
# Expected:l,o and o,w each4; w,</w> count3.
# Exercise 3: Implement a left-to-right nonoverlapping merge.
# Expected:a,a,a,</w> becomes aa,a,</w> and reconstructs aaa.
# Exercise 4: Learn two deterministic merges, rebuilding counts each time.
# Expected:(l,o), then(lo,w), independent of dictionary insertion order.
# Exercise 5: Encode with frozen rules and an explicit unknown-symbol policy.
# Expected:lower/row round-trip, slow raises for unknown s, no merges change.
# Exercise 6: Write a tokenizer/model compatibility record.
# Expected:algorithm,normalization,vocabulary IDs,merges,special tokens and evidence limits.
# Add your code and observations below. Do not download a tokenizer or model.

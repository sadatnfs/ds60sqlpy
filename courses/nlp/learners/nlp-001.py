"""nlp-001 learner workspace. Keep your own attempts in the saved classroom pad."""
from collections import Counter

documents = [
    {"id": "a", "family": "account-reset", "text": "Reset password", "label": "account"},
    {"id": "b", "family": "billing-charge", "text": "Double charge", "label": "billing"},
    {"id": "c", "family": "account-reset", "text": "Password reset please", "label": "account"},
    {"id": "d", "family": "billing-refund", "text": "Refund request", "label": "billing"},
]
print("Documents:", len(documents))
print("Class counts:", dict(Counter(row["label"] for row in documents)))

# Exercise 1: Reject duplicate IDs without mutating documents.
# Expected: four original rows pass; an appended ID a raises ValueError.
# Exercise 2: Reject blank text and a missing family.
# Expected: both invalid fixtures raise ValueError and are not silently dropped.
# Exercise 3: Count documents, class labels and whitespace pieces separately.
# Expected: 4 documents, 2 labels per class and 9 pieces; repeated text changes only pieces.
# Exercise 4: Compare unweighted and length-weighted accuracy.
# Expected: .5 unweighted; 1000/1010 or 10/1010 under the two weight assignments.
# Exercise 5: Audit and repair family overlap without losing rows.
# Expected: original account-reset overlap; a disjoint repair retaining a,b,c,d once.
# Exercise 6: Write a task contract that rejects a fluent summary when a queue label is required.
# Expected: explicit prediction unit, allowed outputs and limits of this tiny corpus.
# Add your functions, assertions, observations and written contract below.

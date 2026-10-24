# nlp-001: Explanatory solutions

These are comparison notes for an independent attempt. The executable companion is `nlp-001_solution.py`. Its assertions cover five computational exercises. Exercise 6 asks for a written task contract and cannot be certified by printing a success message.

## Exercise 1: Validate identity without changing the evidence

Build a `seen` set while visiting the records. Reject a repeated ID before adding it. The set represents identity, so it must not use the text or class label as its key. Two different IDs may contain the same text; whether to deduplicate those is a later policy decision. Conversely, an ID collision is a problem even when the colliding records have different text.

The reference returns the number of accepted IDs but never repairs or deletes rows. A deep copy before validation makes the nonmutation claim inspectable. Comparing only the original list's length would miss an in-place modification to one of its dictionaries. Appending a copied record with ID `a` is a useful negative fixture because the remaining fields are valid, isolating the identity error.

**Expected:** the four original rows pass and remain unchanged. The appended collision raises `ValueError`.

## Exercise 2: Reject invalid records explicitly

There are two checks for each required field: its value must be a string, and its stripped value must contain something. A string of spaces satisfies the first condition but not the second. A missing field fails the type check when `row.get(field)` returns `None`. The reference checks `family` as well as `text` because the proposed evaluation requires family provenance.

This is a deliberately narrow corpus contract. It does not prove the text is in English, the label is correct, or the family annotation is meaningful. If a future task allows blank text or missing provenance, change the specification and associated tests deliberately. Silently dropping the offending rows would conceal a data-quality decision and might alter class balance.

**Expected:** both the all-space text and missing-family record raise `ValueError`; no new filtered dataset is substituted for the input.

## Exercise 3: Count documents, labels and pieces separately

The document count is the number of records. The class histogram consumes exactly one label from each record. The whitespace-piece count consumes every result of `row['text'].split()`. These loops have different units. Keeping their results under explicit keys reduces the risk of reporting the piece count as the number of independent samples.

The original fixture contains 4 documents, 2 account labels, 2 billing labels and 9 whitespace pieces. Repeating the first document's text adds two pieces. It does not add a document or change the label. The reference uses a copied fixture for this intervention, retaining the original for comparison. This is a small controlled experiment on the counting procedure, not an experiment on a real support population.

**Expected:** the changed fixture still has 4 documents and the same histogram, with 11 pieces.

## Exercise 4: Explain what weighting does

The unweighted average is `(1 + 0) / 2 = 0.5`. With lengths `[1000, 10]`, the weighted numerator is `1000*1 + 10*0`, and the denominator is 1010. Reversing the lengths changes the numerator to 10. The correctness indicators have not changed, so the unweighted average remains 0.5.

The correct label is “length-weighted document accuracy.” Calling it token accuracy would invent a token-level prediction task that the example never performed. The reference compares the two fractions using a small absolute tolerance because binary floating-point does not represent every rational number exactly. The tolerance addresses representation error; it does not express uncertainty about a population accuracy.

**Expected:** weighted scores `1000/1010` and `10/1010`, with unweighted accuracy 0.5 in both cases.

## Exercise 5: Repair one leakage mechanism and inspect what remains

The original training family set is `{account-reset, billing-charge}`. The original holdout set is `{account-reset, billing-refund}`. Their intersection contains `account-reset`. Moving both account-reset records together eliminates this overlap. Checking the sorted IDs across both partitions ensures the repair did not quietly lose or duplicate a row.

The reference chooses training records `a, c` and holdout records `b, d` to make family separation obvious. That partition has a serious additional limitation: training contains only account examples and holdout only billing examples. It is a valid demonstration of family disjointness, not a useful classifier evaluation. With only one account family in this toy corpus, it is impossible to put independent account families into both partitions. Collect more independent families rather than interpreting a split constraint as solved by code alone.

**Expected:** empty family intersection and exactly one occurrence of each ID. A complete explanation must also flag the class-coverage problem and tiny holdout.

## Exercise 6: Specify a contract that can reject a fluent wrong answer

For the initial ticket “I forgot my password,” a fluent summary might be “The customer cannot access the account.” That summary communicates relevant meaning, but it is not one of the allowed routing outputs `account` or `billing`. If the consuming system expects a queue label, accept only that schema and treat an unsupported response as a distinct failure or escalation.

The prediction unit is the initial ticket, not every quoted reply. The target definition is the queue policy. The evaluation must compare the system output with independently established labels on the intended deployment units. The tiny authored fixture establishes only that certain program behaviors can be checked. It supplies no defensible estimate of performance on unseen customers, no evidence about languages absent from the fixture and no uncertainty bound on operational errors.

**Expected:** a concrete rejected summary, an allowed-output rule and an explanation of the evidence limits. This written reasoning remains separate from automated execution.

## Transfer after comparison

Create a new fixture containing two distinct document IDs with identical text and different annotation versions. Explain which identity checks should pass, which provenance question requires review and whether either row belongs in a holdout used to evaluate the other. The point is to separate data representation, evaluation design and model quality rather than compress all three into a single pass flag.

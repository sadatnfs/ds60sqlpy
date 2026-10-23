# nlp-003: Explanatory solutions

The executable companion implements a narrow invoice policy with inspectable spans. It does not validate whether an invoice exists or whether an action involving it is authorized. Exercise 6 requires written interpretation in addition to the five computational checks.

## Exercise 1: Preserve the evidence location

The first reference starts after `Pay `, at index 4, and occupies eight code points, ending at 12. The second starts at 26 and ends at 34. A half-open range makes the substring length equal to `end - start`. The named capture contains only the four digits, while group 0 contains the entire match. Keeping both avoids accidentally treating the digits as the raw extracted phrase.

The reference checks the exact tuples and verifies each slice against the original message. A check that only compares a list of identifiers would miss an offset bug. A downstream reviewer needs the span to see the source evidence, and a later normalization step must not silently change which text version those coordinates refer to.

**Expected:** the two full matches, digit strings `1042` and `9012`, and spans `(4,12)` and `(26,34)`.

## Exercise 2: Build counterexamples that distinguish rules

The five-digit reference tests whether the implementation accepts a valid prefix inside a longer number. The letter and underscore prefixes test the leading word-boundary rule. The full-width digits test whether the pattern implements the declared ASCII digit contract rather than a broader Unicode decimal class.

The parenthesized valid reference is a control. Without a positive control, a broken extractor that returns nothing could pass every negative test. These cases are original teaching fixtures and do not establish performance on all possible invoice formats. If production requirements allow a previously rejected form, update the specification, annotations and regression expectations together.

**Expected:** no match for the four invalid forms, and one valid `INV-1042` match inside parentheses.

## Exercise 3: Match the API to the task

A message can contain a reference after introductory text, so `search` succeeds there while `match` does not. An ID-only field is valid under `fullmatch` only if no extra characters remain. An implementation that searches the field and returns its first matching substring changes the contract: it accepts an invalid field by discarding evidence that the input was malformed.

The guide deliberately uses a simple pattern without boundaries for these API comparisons so the difference comes from where and how much of the string the API examines. A complete field validator would still apply semantic checks such as the all-zero exclusion. Passing a regex is one step in validation, not a universal certification of the value.

**Expected:** `True`, `False`, `True`, `False` for the four calls in the worked example.

## Exercise 4: Separate candidates, exclusions and canonical IDs

The improved candidate pattern names ordinary ASCII cases explicitly. The semantic filter rejects the captured digit string `0000`. Canonicalization combines the uppercase prefix with the unchanged digit string. The raw substring and span remain tied to the original text. Converting the numeric part to an integer would unnecessarily lose leading zeros from a valid identifier such as `INV-0012`.

The third worked message contains three kinds of candidate. The all-zero one has the right syntax but fails the policy. The lowercase one satisfies the policy after prefix canonicalization. The five-digit one does not satisfy the syntax. Recording those reasons separately makes error analysis more useful than reporting only a final empty or nonempty result.

**Expected:** exactly the `inv-7777` record at `(10,18)`, canonicalized to `INV-7777`, with the input string unchanged.

## Exercise 5: Score entity identities at the declared granularity

An entity tuple includes document identity, start, end and canonical ID. Intersecting the predicted and gold sets finds two exact agreements. One prediction is absent from gold, and one gold item is absent from predictions. Precision and recall therefore have the same numeric value, 2/3, for different denominators.

Moving a predicted reference to another document must break the match even when its text and local offsets remain identical. Dropping the document ID from the evaluator would incorrectly combine unrelated evidence. The helper returns `None` when a metric's denominator is zero. That is an explicit convention, not an implied zero or perfect score. A report should show TP, FP and FN so the reader can interpret such cases.

**Expected:** TP=2, FP=1, FN=1; precision and recall 2/3. Moving one correct entity to another document reduces TP to 1.

## Exercise 6: A mention is not an authorized action

“Please pay INV-1042” and “Do not pay INV-1042” contain the same reference. The extractor correctly finds it in both messages. The requested action differs because of context that this extractor does not model. Even a perfect intent classifier would not establish that the sender may authorize payment or that the invoice exists and is payable.

A complete action workflow would need a defined intent representation, source identity, authorization checks, invoice state and an explicit execution boundary. In the classroom, the lesson stops at extraction and explanation. It never calls an external financial service. A subject-matter assistant should make the same separation between retrieved or extracted evidence and any consequential action.

**Expected:** both mentions are extracted, and the written answer identifies the additional evidence rather than interpreting extraction success as action approval.

## Transfer after comparison

Create one new false positive caused by a format assumption and one semantic ambiguity that no format-only rule can resolve. Keep them separate in the error ledger. Then describe how a changed annotation policy would affect both the gold set and the measured precision/recall. Do not tune the extractor while leaving the evaluation contract implicit.

# Turn Messy Text into Trustworthy Records: solution reasoning

Stable ID: `python-foundations-03`.

Read the [guide](../companion-guides/py_foundations_03_clean_records.md) and attempt the [learner artifact](../lessons/py_foundations_03_clean_records.py) first. The [executable solution](py_foundations_03_clean_records_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The reference separates parsing, record validation, and batch policy.
That makes a failed rule visible and lets each layer have a small test. The
first two functions raise ValueError for an input that violates the declared
contract. The batch layer catches that specific signal and records the failed
row instead of losing the entire batch. Unexpected errors still escape.

```python
rows = [{"id": "A", "quantity": "2"}, {"id": "B", "quantity": "many"}]
# After cleaning: accepted count 1, rejected count 1, accepted total 2.
# Independent accounting: 2 == 1 + 1.
```

Record order is preserved. The solution copies raw dictionaries into rejection
records and creates fresh canonical dictionaries for accepted rows. It makes
no claim that mutable nested data would be fully isolated by a shallow copy.

## Exercise 1. Define the policy before coding

The parser first checks that the supplied object is a nonempty string after whitespace removal. Conversion then distinguishes integer text from decimal or arbitrary words. A negative integer is syntactically valid but violates the quantity rule, so it gets a different reason. Zero is valid and is returned as zero. The reference deliberately accepts a leading plus sign because Python integer conversion accepts it and our contract discloses it. If a stricter external format is required later, add a lexical rule and tests rather than assuming this parser enforces one.

## Exercise 2. Keep raw records unchanged

Normalize the identifier with strip and parse the quantity into a new dictionary. Keep the original object untouched. The input contains the only direct evidence that surrounding spaces existed, so mutating it would remove information useful for troubleshooting. Compare both canonical values and original values in a test; checking only the returned result would miss unwanted mutation. These records contain simple text fields, which is why a shallow dictionary copy is enough for rejection evidence. That argument must be reconsidered if the record schema changes.

## Exercise 3. Make missing identity visible

Absent keys are inspected with get, then validated as text with nonempty content. An absent key returns None and is rejected instead of becoming the displayed string "None". Case-sensitive identity means A and a remain distinct. That is a policy choice, not a universal rule for identifiers. Trimming normalizes outer spaces without changing internal characters or case. If a future source uses case-insensitive identities, treat that as a deliberate migration because previously separate records may collide. Preserve the original values while investigating those collisions.

## Exercise 4. Account for every row

For each source row, use enumerate with start one to record a human-readable row number. A valid canonical record goes into accepted; a validation failure goes into rejected with its raw copy and reason. Quantities two and zero sum to two, while many is rejected at row two. The three-way evidence checks count conservation, value correctness, and reject location independently. A program that copies one row twice could accidentally pass a total-only check, so preserve row counts and identities as well as aggregate values.

## Exercise 5. Enforce first valid wins

The seen set is updated only after a valid record passes all checks. A/many fails conversion and therefore never reserves A. A/2 becomes the first valid record and is accepted. A/3 is then rejected as a duplicate. This explicitly implements first-valid-wins, which differs from first-row-wins and last-row-wins. The original third row stays visible in rejected evidence. If the two valid rows disagree, the policy does not claim the first is factually correct; it provides deterministic behavior and enough evidence to review the conflict.

## Exercise 6. Reject wrong field types

A None quantity violates the text representation boundary. A numeric identifier violates the identifier representation boundary. Converting arbitrary values with str would hide those distinctions, and int(True) would create another surprising coercion if booleans were accepted. The reference uses explicit string checks so its numeric policy only operates on declared text input. Tests should assert that both invalid records are rejected and that raw values remain None and integer three, respectively. That catches accidental coercion even if the final counts still reconcile.

## Exercise 7. Check empty and all-invalid batches

An empty input has zero accepted rows and zero rejected rows. A batch containing two invalid rows has zero accepted rows and two rejected rows. Both accepted totals are zero, but they describe different situations and must retain different counts. Summing with a zero start makes the intended identity element explicit and avoids a reduction that crashes on empty input. A report should show counts beside totals so a reader cannot mistake a zero quantity after total rejection for a successfully observed zero quantity.

## Exercise 8. Transfer to stock adjustments

A signed adjustment stream models a different meaning: negative quantities can be legitimate returns. Keep a separate parser or explicit policy parameter instead of quietly changing the shared nonnegative contract. Both versions should still reject missing input and decimal text when exact integers are required. Write normal, zero, negative, and invalid cases for each policy. The key learning is that validation follows meaning. There is no single universal cleaning rule that correctly handles inventory counts, financial adjustments, temperatures, and event counters without domain-specific decisions.

## Compare and transfer

Change the batch order and predict which accepted quantity wins under first-valid-wins. Then ask whether order independence is a requirement for your real source. If it is, the duplicate policy must change, perhaps to reject every conflicting identity or require an explicit version. Do not describe deterministic order-sensitive behavior as evidence of order independence.

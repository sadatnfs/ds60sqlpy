# Build Your First Auditable Data Investigation: solution reasoning

Stable ID: `python-foundations-04`.

Read the [guide](../companion-guides/py_foundations_04_first_investigation.md) and attempt the [learner artifact](../lessons/py_foundations_04_first_investigation.py) first. The [executable solution](py_foundations_04_first_investigation_solution.py) is a comparison implementation. It does not certify your changed program merely because its own demonstration succeeds. Copy the acceptance cases into your attempt, then change one input without changing the intended policy.

The reference uses a pure analysis function between two small file
boundaries. Loading validates the exact header rather than guessing at column
names. Analysis rejects declared input defects and makes row accounting
visible. Report writing is tested through a temporary JSON file and readback.
The demonstration does not write learner progress or modify the fixture.

```python
assert 7 == 4 + 3
assert 11 == 7 + 0 + 4
```

These arithmetic observations are intentionally independent of the helper
implementation. They give a small human-checkable oracle. For a large source,
the oracle would need a carefully sampled manual audit and broader invariants,
not a claim that agreement among two copies of the same calculation proves
every input record correct.

## Exercise 1. Write a project charter

The charter asks for recorded accepted units by region, using the three tracked columns and the declared validation and duplicate rules. It promises grouped integer totals, source/accepted/rejected counts, and specific rejection evidence. It does not promise complete demand measurement or correct missing source records. Writing those boundaries first prevents a later chart title from claiming more than the input can establish. A useful unanswered question is why records contain invalid quantities and whether the duplicate id represents a correction, a replay, or an upstream defect.

## Exercise 2. Load the tracked CSV

DictReader returns one dictionary per data row. Open with explicit encoding and newline="" so behavior is portable, then compare fieldnames with the required sequence. The teaching contract rejects reordered, missing, or extra columns instead of guessing. An entirely different contract could allow reordered headers, but its tests would need to say so. The tracked fixture yields seven data rows. The header is not counted as a data row; rejection row numbers in this lab refer to data rows, not physical line numbers in arbitrary quoted CSV.

## Exercise 3. Validate and retain rejection evidence

Validate id and region before using their string methods. Parse quantity and reject negatives. Only after all fields succeed should the identifier enter the seen set. Rejected rows retain their one-based data-row number, reason, and a copy of raw fields. The fixture rejects many at row four, duplicate b at row five, and negative quantity at row six. Accepted rows are a, b, c, and f. A test comparing the original list with an untouched copy detects accidental normalization in place, even when final aggregate totals look right.

## Exercise 4. Aggregate to one result per region

The accepted north quantities two and five sum to seven. The accepted south quantity zero creates a real south entry with total zero. West contributes four from f; the invalid west rows contribute nothing to accepted units but remain in rejection evidence. Total accepted quantity is eleven. The second b row is a duplicate and does not add three. Sorting dictionary keys helps deterministic display and JSON comparison; it does not change the identity or arithmetic policy. Avoid filtering values with if quantity because zero is valid.

## Exercise 5. Add independent checks

Check source-row accounting before looking at totals: seven equals four plus three. Then check that group totals sum to eleven and compare the manual fixture calculation. Empty input yields zero counts, zero units, and no groups. An all-invalid batch also yields zero units but positive input and rejected counts. Those checks reveal different mechanisms. Do not derive input_count from accepted plus rejected and then call their equality an independent test; count the original source rows so a dropped row can make the assertion fail.

## Exercise 6. Write and read a local report

The writer serializes a dictionary with standard JSON-compatible fields, sorted keys, readable indentation, and a trailing newline. The caller supplies the path, and the writer deliberately creates its parent. A temporary directory makes the reference readback safe and repeatable. Compare loaded JSON content with the report rather than only checking that the file exists. File presence proves much less than content equality. The lab does not claim atomic publication or crash durability; the advanced restartable-pipeline module introduces those additional guarantees and limitations.

## Exercise 7. Challenge the duplicate policy

For two valid rows sharing one id, the first is accepted and the second rejected. Reversing their order changes which quantity wins. That result is consistent with first-valid-wins and demonstrates its order sensitivity. If order independence were required, the policy would need a stronger identity/version contract or conflict rejection. Do not hide the discrepancy by sorting solely to make a preferred quantity first. Preserve the conflicting raw row and explain why a real ingestion system should understand whether it represents correction or accidental duplication.

## Exercise 8. Present a reproducible conclusion

A reproducible conclusion gives the exact command, observable test result, accepted total eleven, four accepted rows, and three rejected rows. It also states the validation and duplicate policies and limits the claim to this input. Running a new process checks for hidden session state. It does not certify every operating system or the truth of the source data. A responsible next step would investigate the rejected records with the source owner or add an explicit correction/version field. More elaborate graphics cannot resolve missing source meaning by themselves.

## Compare and transfer

Create a separate temporary input with one valid zero row and compare it with an empty input. Both totals are zero; their source counts and region mappings differ. Present those differences in plain language. Then replace first-valid-wins with conflict rejection in a copy and identify every test whose expected result must change because the policy changed.

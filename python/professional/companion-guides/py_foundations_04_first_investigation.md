# Build Your First Auditable Data Investigation

**Stable ID:** `python-foundations-04`

**Estimated time:** 210 minutes, split across sessions as needed.

## Level and prerequisites

Foundation. Direct catalog prerequisites: `python-foundations-03`, `python-10`.

You can read CSV, write small functions, validate text records, and run assertions or pytest. This is a project checkpoint, not a race. Complete the stages over several sessions before moving into larger data libraries.

## Learning objectives

- Turn a question into a small, testable project charter.
- Separate loading, validation, summarizing, and reporting.
- Build a local report with counts, totals, rejection evidence, and limitations.
- Reproduce a result from a fresh process and explain what it proves.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional contributor route:** use the prepared environment in
[CONTRIBUTING](../../../CONTRIBUTING.md) on Linux, macOS or Windows through
WSL 2. The commands below assume its packages are already installed. They are
not prerequisites for opening this lesson in the Docker classroom. Local
`.learning/` files and CLI progress belong to this checkout; they do not read or
update the Docker classroom's named learning volume.

Use the repository folder in VS Code. The rendered lesson page is a preview;
edit the actual [learner script](../lessons/py_foundations_04_first_investigation.py). Copy it to an ignored
folder under `.learning/` first if you want to keep your attempt across course
updates. Use the interpreter from setup. These examples need only Python's
standard library, have no network calls, and use the same inputs on each run.

Prepared POSIX/WSL contributor terminal:

```sh
uv run --no-sync python python/professional/lessons/py_foundations_04_first_investigation.py
```

The terminal shows a small worked example and the remaining TODO count.
TODOs are the starting exercise state. Write predictions before changing
code. Run after one change, save the observed value or exception, and compare
with the exercise's acceptance check. A successful example does not mean the
unfinished exercises are complete. Keep the separate
[explanatory solutions](../solutions/py_foundations_04_first_investigation_solutions.md) and
[runnable solution](../solutions/py_foundations_04_first_investigation_solution.py) closed until you have an
attempt and evidence, or deliberately ask for a worked comparison.

## Vocabulary and concepts

An investigation connects a question to evidence that another person can
inspect. Our question is: how many accepted units are recorded for each region
in this small source file? This is deliberately narrower than estimating true
regional demand. Invalid records, duplicate policy, and absent regions limit
what the result can claim. Treat the pipeline like a chain of receipts: each
stage names its input, output, and the check that connects them.

- **Charter:** a short statement of the question, inputs, assumptions, and
  acceptance criteria for a project.
- **Stage:** one operation with a clear boundary, such as reading text or
  aggregating validated records.
- **Aggregate:** a summary calculated from several records, such as a total.
- **Artifact:** a file produced so someone else can inspect or reuse a result.
- **Provenance:** information connecting a result to its input and rules.
- **Limitation:** a condition that prevents a broader conclusion from being
  supported by the evidence available.

The tracked [beginner orders CSV](../fixtures/data/beginner_orders.csv) has
seven records. Required columns are `id`, `region`, and `quantity`. Strip outer
spaces from id and region, keep both case-sensitive, require nonempty text,
and parse a nonnegative integer quantity. Keep the first valid id. Preserve a
source row number and raw dictionary for every rejected row. A zero-quantity
record remains valid and its region must appear with a zero total if it has
no other accepted units.

Do not write a single giant function that reads, cleans, prints, and saves.
Start with `load_rows(path)`, `analyze_rows(rows)`, and `write_report(report,
path)`. The middle function should depend on data values, not a terminal or
current directory. That makes boundary tests possible without repeatedly
creating files. The I/O functions can then be tested using temporary paths.

## Worked example / walkthrough

### Example A: total after validation, including a real zero

```python
records = [
    {"id": "A", "region": "north", "quantity": 2},
    {"id": "B", "region": "south", "quantity": 0},
    {"id": "C", "region": "north", "quantity": 5},
]
by_region = {}
for record in records:
    region = record["region"]
    by_region[region] = by_region.get(region, 0) + record["quantity"]
assert by_region == {"north": 7, "south": 0}
```

The dictionary key is the region; the value is its accumulated integer units.
`get(region, 0)` uses zero only for a group not previously encountered. It does
not replace invalid input with zero. A valid south record creates the south
entry even though adding its quantity does not increase the total. Expected
observation: two regions, with north seven and south zero.

### Example B: verify a report independently

```python
report = {
    "input_count": 7,
    "accepted_count": 4,
    "rejected_count": 3,
    "total_quantity": 11,
    "by_region": {"north": 7, "south": 0, "west": 4},
}
assert report["input_count"] == report["accepted_count"] + report["rejected_count"]
assert report["total_quantity"] == sum(report["by_region"].values())
print(report["total_quantity"])
```

Expected output is 11. The first assertion checks row conservation; the second
checks aggregation conservation. Neither alone proves the input is truthful.
Add a manual calculation for this tiny fixture: two plus zero plus five plus
four equals eleven. Different checks should challenge different defects. If
every check simply calls the same summarizing helper, a bug in that helper
could make all checks agree with the same wrong answer.

### Reproduction is a feature of the project

Use `Path` for file names and an explicit UTF-8 encoding. Resolve the tracked
fixture from the documented repository root. When running from another folder,
pass its explicit path to `load_rows`; a copied learner script can still use
the same repository-root command. Open CSV with `newline=""` so the csv module controls newline
handling on Windows as well as POSIX systems. JSON output should contain only
plain values, sorted keys, and a trailing newline for inspectable diffs.

Keep learner output under `.learning/` or `artifacts/`. The reference
demonstration uses a temporary directory that is removed automatically. Never
write over the tracked fixture to make a test easier. A written report should
name the input contract and contain rejected rows, because an accepted total
without its discarded-data context can be misleading. A graph is optional:
the first goal is a report whose meaning and accounting you can defend.

At the final checkpoint, close the terminal and run the project again. A
result that requires manually executing fragments in a lucky order has a
hidden-state problem. Capture the command, report values, and test result.
State whether you tested your own implementation or only ran the reference.

## Exercises

1. **Write a project charter.** Write five sentences naming the regional-units question, tracked input, first-valid-id policy, output fields, and a limitation about rejected records.

   **Verify:** The charter names the three columns and explicitly avoids claiming that accepted units equal true demand or that absent regions had zero demand.

   **Hint:** A precise small question is easier to finish than an undefined analysis.

2. **Load the tracked CSV.** Implement `load_rows(path)` using DictReader, UTF-8, and newline handling. Require the header sequence id, region, quantity.

   **Verify:** The tracked file loads seven dictionaries in source order; a header lacking region raises ValueError before analysis.

   **Hint:** Check fieldnames once at the file boundary.

3. **Validate and retain rejection evidence.** Implement `analyze_rows` with nonempty id/region text, nonnegative integer quantity, and first-valid-id wins. Preserve inputs.

   **Verify:** The fixture has four accepted rows and rejects source rows 4, 5, and 6. Raw records remain byte-for-byte equivalent as string values.

   **Hint:** Reuse the prior lesson policy in your own code, but keep this project runnable as a single file.

4. **Aggregate to one result per region.** Add by_region and total_quantity to the report. Keep valid zero-quantity regions and sort region keys for display.

   **Verify:** The mapping equals north 7, south 0, west 4; the total is 11. No duplicate record contributes three extra units.

   **Hint:** Aggregate accepted rows only; a zero adds a group even when it adds no units.

5. **Add independent checks.** Write tests for count reconciliation, sum-of-groups reconciliation, and the tiny fixture manual total. Add empty input and one all-invalid batch.

   **Verify:** The fixture checks are 7 = 4 + 3 and 11 = 7 + 0 + 4; empty input has all counts zero and an empty mapping.

   **Hint:** Choose checks that fail for different possible mistakes.

6. **Write and read a local report.** Implement `write_report` to UTF-8 JSON at a supplied learner-local path, then load it and compare content with the in-memory report.

   **Verify:** The JSON round trip preserves counts, grouped totals, and rejected row numbers; no tracked source file changes.

   **Hint:** Serialize plain dict/list/int/string values and create the output parent directory deliberately.

7. **Challenge the duplicate policy.** Analyze two valid rows with the same id but different quantities, then reverse them. Explain the effect without claiming a bug in summation.

   **Verify:** For duplicate id A with quantities 2 then 5, assert total_quantity 2; reversal yields 5. Both results report rejected_count 1, proving the order-sensitive policy.

   **Hint:** Separate an intentional identity policy from arithmetic behavior.

8. **Present a reproducible conclusion.** Run your own script from a new process, record its command and checks, and write a short conclusion with result, quality counts, and one unanswered question.

   **Verify:** The conclusion states 11 accepted units, four accepted rows, three rejected rows, and the inability to establish actual demand from this source alone.

   **Hint:** Name what your evidence supports before discussing what you would collect next.

## Self-check

Explain why an accepted total of zero can mean a valid zero, an empty source,
or an all-rejected source. Which report fields distinguish those cases? Trace
one duplicate through the stage boundaries. Rebuild one test using only a
two-record in-memory fixture and explain why it does not need filesystem I/O.

## Common pitfalls

If running from another folder loses the fixture, inspect how the default
path is derived. If south disappears, check whether a truthiness filter removed
quantity zero. If totals are fourteen, inspect duplicate acceptance before
changing aggregation. If count checks pass after dropping a rejection, check
whether input_count was incorrectly calculated from output rather than source.

## Next step

Keep this small project as a reference for the CLI project and the later pandas
EDA project. Add packages only when they solve a named limitation; preserve
the plain-data tests and policy explanations when changing the implementation.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for python-foundations-04.
Read python/professional/companion-guides/py_foundations_04_first_investigation.md and python/professional/lessons/py_foundations_04_first_investigation.py.
Check my direct prerequisites: python-foundations-03, python-10.
Keep solutions/ closed unless I request comparison after an attempt.
Explain the mental model, ask me to predict one result, let me attempt it,
give one hint at a time, inspect my evidence, and ask a retrieval question.
Done when I can independently reproduce the numbered acceptance checks,
explain a failure case, and transfer the policy to a changed input.
```

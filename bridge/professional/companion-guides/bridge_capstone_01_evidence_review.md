# BRIDGE-CAPSTONE-01: Evidence-Driven Data Product and Incident Review

## How to run this lesson

This capstone runs offline with the Python standard library. It does not open a
database, contact a service, publish a real product, or download a dataset.
Work from the repository root with the course interpreter. Open the
[answer-free learner](../lessons/bridge_capstone_01_evidence_review.py) in VS
Code, read its types, and run its supplied `main()` once. It prints a scenario
orientation and performs no unfinished exercise. A successful starter run is
orientation evidence, not proof that you completed the eight exercises.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython bridge\professional\lessons\bridge_capstone_01_evidence_review.py
```

macOS/Linux:

```bash
.venv/bin/python bridge/professional/lessons/bridge_capstone_01_evidence_review.py
```

Use VS Code's **Save As** to create a new `work/capstone_attempt.py` if you want
to preserve the official starter. Choose an unused name and retain its
repository-relative `FIXTURES` path. Run the copy from the repository root.
Write your own tests in `work/test_capstone_attempt.py`, importing your attempt,
then run `python -m pytest -q work/test_capstone_attempt.py` with the same
course interpreter. The supplied focused tests import the reference solution;
passing those tests verifies the repository reference, not your unimplemented
copy. After attempting the exercises, compare the separate
[solution reasoning](../solutions/bridge_capstone_01_evidence_review_solutions.md)
and [executable reference](../solutions/bridge_capstone_01_evidence_review_solution.py).

If imports or paths fail, verify the repository-root working directory before
changing code. If the interpreter is missing, return to operating-system setup
and the course doctor. There is no database readiness step for this module.
Any future live extension must follow the bridge's local disposable
`advanced_sql_training` boundary, typed values, and explicit transaction rules;
it is not part of this default capstone.

## Level and prerequisites

- **Level:** Advanced integrated capstone.
- **Direct catalog prerequisites:** `bridge-08` ([integration review](../../companion-guides/day08_production_capstone.md)), `sql-quality-01` ([bag reconciliation](../../../sql/professional/companion-guides/sql_quality_01_bags_and_fanout.md)), and `python-pro-03` ([restartable file pipeline](../../../python/professional/companion-guides/py_pro_03_restartable_file_pipeline.md)).
- **Prerequisite skills:** immutable records, exact integer amounts, injected
  effects, fake tests, keyed equality, and recovery evidence.
- **Artifacts:** learner, explanatory solution, executable solution, three
  synthetic JSON fixtures, and focused fake-backed tests.

## Learning objectives

- Reject an apparently healthy release using independently expected identities
  and values instead of matching grand totals alone.
- Repair a data product from source facts without changing the golden answer to
  fit the implementation.
- Gate a fake publication, preserve an inspectable review artifact, and explain
  the difference between a tested repair and an observed production recovery.

## Vocabulary and concepts

Imagine a finance export with three invoice rows. Its release summary says
three invoices and 15,000 cents. An independent expected fixture says the same.
The controls look reassuring, but the release understates invoice B, omits
zero-valued invoice C, and invents invoice D. One error cancels another in the
grand total. Your job is to make that failure visible, repair the transform,
and write a review whose claims stay within the available evidence.

**Data product:** A dataset delivered under a declared contract, including its
grain, identities, field meanings, and allowed values. Here one row represents
one invoice identified by `invoice_id`, and money is nonnegative integer cents
in one synthetic currency. Missing invoices differ from zero-valued invoices.

**Golden fixture:** A small independently specified expected result. It is
checked in separately from the implementation. Rebuilding it by calling the
same transformer under test would destroy that independence. A golden fixture
is only evidence for the cases and domain assumptions it actually covers.

**Reconciliation:** A comparison that reports changed matched identities,
missing expected identities, and unexpected actual identities. Check both
directions. Validate unique identities first; a dictionary silently discarding
a duplicated invoice is a hidden policy decision, not reconciliation.

**Canonical fingerprint:** A digest of a declared deterministic encoding of the
contract version and validated rows. Sorting identities makes row presentation
order irrelevant to this product's equality. A digest identifies encoded
content; it does not make the content correct, establish who produced it, or
provide a signature or trusted custody chain.

**Publication gate:** The point before an external effect at which required
evidence is checked. In this lesson the effect is an injected fake publisher.
The gate controls whether that fake is called; it does not simulate a database
commit, message broker acknowledgement, or actual consumer delivery.

**Incident review:** A record that separates observations, impact, causal
claims, corrective action, verification, and unresolved questions. A plausible
historical explanation is still a hypothesis when the source release code and
timeline are absent. No person or service should be blamed based on these
synthetic snapshots.

## Syntax anatomy and ownership

The supplied frozen dataclasses describe values: `ProductRow` is an invoice,
`SourceLine` is a line item with its own identity, and `Difference` records one
invoice-level mismatch. `None` in a diagnostic means one side lacks that
invoice. It is not an unknown amount inside a valid product; the product
contract requires an integer amount. `type(value) is int` deliberately rejects
Boolean values because Python otherwise treats `True` as an integer.

`Sequence[ProductRow]` permits caller-owned input collections. Validate and take
an immutable tuple snapshot before review and publication so later caller
mutation cannot change what is emitted. A `Publisher` Protocol describes a
method the caller supplies. It does not create an external connection. Tests
provide an implementation that records calls, allowing you to inspect the
exact release ID, reviewed rows, and digest without a service.

Keep effects at the boundary. Parsing reads a caller-named file; transformation
and reconciliation return values; publication calls the injected adapter only
after exact checks. The report writer receives a caller-supplied path and uses
exclusive creation. It refuses an existing path rather than overwriting
learner work. Exclusive creation protects existing bytes; it is not an atomic
multi-file publication protocol and a process crash can leave an incomplete
new report. Detect and investigate a partial artifact rather than trusting its
filename as proof of completion.

## Worked example / walkthrough

### Example 1: A passing total with a failing keyed result

This complete example needs only Python. Predict both prints first:

```python
expected = {"X": 100, "Y": 50}
observed = {"X": 90, "Y": 60}
print(sum(expected.values()), sum(observed.values()))
changed = [key for key in sorted(expected) if expected[key] != observed[key]]
print(changed)
assert sum(expected.values()) == sum(observed.values())
assert changed == ["X", "Y"]
```

**Expected:** The first print is `150 150`; the second is `['X', 'Y']`.
The input grain is one amount per invoice key. Summing removes identity, so
equal sums cannot prove invoice equality. This tiny example assumes identical
key sets. The capstone must additionally handle missing and unexpected keys,
validate input uniqueness before dictionary conversion, and keep zero distinct
from an absent invoice.

### Example 2: Evidence controls an injected effect

This complete toy model uses only lists and dictionaries:

```python
journal = []


def checked_record(expected, candidate):
    if expected != candidate:
        return False
    journal.append(tuple(sorted(candidate.items())))
    return True


assert checked_record({"X": 100}, {"X": 90}) is False
assert journal == []
assert checked_record({"X": 100}, {"X": 100}) is True
assert journal == [(("X", 100),)]
print(len(journal))
```

**Expected:** It prints `1`. Rejection happens before the fake effect, and a
passing comparison records the reviewed value exactly once. This toy is
purposefully narrower than the capstone: it has no file parsing, duplicate
validation, release identity, fingerprint, or failure-after-effect behavior.
The full exercise makes those boundaries explicit. A fake journal is evidence
of call ordering, not proof of a real release or exactly-once delivery.

## Exercises

Keep predictions and actual test results in your attempt. The three files in
`bridge/professional/fixtures/capstone/` are synthetic course data. Do not edit
the golden fixture to make a failing implementation pass. Start with literal
assertions whose expected values are written independently of your function.

1. **Validate the product boundary.** Implement `normalize` and `load_product`.
   Require exactly `invoice_id` and `amount_cents` per JSON row, unique nonempty
   invoice IDs without outer whitespace, and nonnegative integer cents. Reject
   Boolean amounts, fractional values, missing/extra fields, and duplicate IDs.

   **Expected:** Golden rows are `(A,10000),(B,5000),(C,0)`, sorted by ID. Each
   malformed fixture raises `ValueError`. Empty input yields an empty tuple;
   a zero-valued invoice remains present. Hint: validate before constructing an
   identity dictionary so duplicates cannot disappear silently.

2. **Retain controls without overstating them.** Implement `summarize` for both
   product fixtures. Write the strongest statement the two controls support,
   then one equality claim they do not support.

   **Expected:** Both inputs yield `Summary(3,15000)`. The expected and incident
   row collections are unequal. Your test must show both matching summaries
   and unequal keyed rows. Hint: a counterexample needs a passing control and
   a failing stronger claim on the same input.

3. **Reconcile identities and values.** Implement `reconcile` and the evidence
   `accepted` property. Validate both inputs, inspect the union of their keys,
   and return deterministic `changed`, `missing`, and `unexpected` diagnostics.
   Keep absent-side amounts as `None`, never zero.

   **Expected:** Exactly three diagnostics, ordered by invoice ID: B changed
   `5000 -> 4000`, C missing `0 -> None`, D unexpected `None -> 1000`.
   `reconcile((), ())` accepts; golden versus golden accepts. Hint: test key
   presence before comparing the associated amount.

4. **Repair from source facts.** Implement `load_source_lines` and
   `build_product` using the independent source-lines fixture and complete
   invoice manifest `('A','B','C')`. Reject repeated line IDs, orphan lines,
   repeated manifest IDs, and invalid cents. Preserve zero-line invoices.

   **Expected:** Repaired rows equal the unchanged golden rows exactly, and
   source inputs remain unchanged. Two A lines sum to 10000, B is 5000, and C
   is 0. A duplicate L1 or a line for absent invoice Z raises `ValueError`.
   Hint: the manifest defines all parent identities; line facts supply amounts.

5. **Fingerprint the declared contract.** Implement `canonical_digest` using
   SHA-256 of UTF-8 canonical JSON containing `contract_version: 1` and sorted
   validated rows. Use sorted object keys, compact separators, and ASCII-safe
   JSON encoding. Explain why this identifies content without proving truth.

   **Expected:** Reordering valid rows preserves the 64-hex digest; changing
   any amount changes it. The golden digest is
   `fddc2c8909fee69e1b96661b9e11a1e87c7212bfe2d5f731a9f45ed2ae868fc3`.
   Repeated invoice identities fail before hashing. Hint: define the bytes
   before selecting a hash function.

6. **Gate a fake publication.** Implement `publish_checked`. Validate the
   release ID, snapshot actual rows once, reconcile with the independent
   expected rows, and call the injected Publisher only after acceptance. Let
   publication failures propagate without automatic retries.

   **Expected:** Incident input raises `ReleaseRejected` with zero recorded
   calls. Repaired input records one `(release_id, sorted_rows, digest)` call.
   A fake that records and then raises still records only once; the caller
   receives the exception and cannot claim acknowledged publication. Hint:
   distinguish a rejected precondition from an unknown external outcome.

7. **Preserve an inspectable artifact.** Implement `write_evidence` to create a
   caller-named JSON report exclusively. Record the contract version, verdict,
   both summaries, both digests, and ordered diagnostics. Use a temporary test
   directory, not a fixed learner output path.

   **Expected:** The report round-trips with `accepted: false` and C's absent
   actual amount as JSON `null`. A second write to the same path raises
   `FileExistsError`, leaving the first report's bytes unchanged. Hint:
   exclusive creation protects existing work without a prior existence check.

8. **Write an evidence-bounded incident review.** Implement `incident_review`
   and prepare a short handoff with observations, impact, causal uncertainty,
   repair, verification, and unresolved questions. Require a rejected before
   and accepted after that both use the same golden digest.

   **Expected:** The review names all three mismatches, explains matching
   summaries, marks the historical cause unproven, and states that consumer
   delivery and production recovery remain unknown. Passing a different golden
   dataset as the repair is rejected. Hint: a working repair can be verified
   even when the original failure mechanism has not been established.

## Self-check

- What information disappears when an invoice relation becomes a grand total?
- Which fixture independently specifies expected behavior, and what would make
  that independence circular?
- Why are `None` and zero different in the C diagnostic?
- Which evidence proves a tested repair, a fake publication call, and actual
  consumer recovery respectively? Which is absent here?
- Without reading the implementation, describe the next negative fixture you
  would add for a new domain requirement.

## Common pitfalls

- **A summary passes while the release is wrong.** Inspect identity-level
  differences for B, C, and D. Do not change the total or the golden fixture to
  hide the discrepancy.
- **Duplicate rows vanish.** Look for a dictionary comprehension before key
  validation. Add two rows with the same ID and require an explicit failure.
- **C disappears because it has no lines.** Check whether the transform starts
  from child lines instead of the complete invoice manifest. A zero-valued
  parent is still a required row.
- **A publication error triggers a second call.** Use the fake that records
  before raising. Its first effect may already have happened, so a generic
  retry is not safe evidence of exactly-once behavior.
- **All tests pass without an attempt.** Inspect the test import. The supplied
  suite exercises the reference; point your own test at the learner copy.
- **The review invents a root cause.** Compare each claim with the supplied
  snapshots and source fixture. Label a hypothesis when no release code or
  deployment timeline proves it.

## Next step

Keep a small portfolio record containing your attempted code, independent tests,
rejected incident evidence, accepted repair evidence, and a bounded incident
review. Extend the contract only after writing a new independently expected
case. For example, adding multiple currencies needs currency in the identity
or grouping contract and must not silently add unlike amounts. Live database
integration is a separate opt-in project with its own transaction and recovery
evidence.

## Ask Codex about this lesson

The guide, fixtures, and local Python tests are sufficient offline. Copy this
optional prompt for coaching:

```text
Tutor me through bridge-capstone-01: Evidence-Driven Data Product and Incident Review.
Use the checked-in $guide-ds60sqlpy-learning skill.
Guide: bridge/professional/companion-guides/bridge_capstone_01_evidence_review.md
Answer-free learner: bridge/professional/lessons/bridge_capstone_01_evidence_review.py
Direct prerequisites: bridge-08, sql-quality-01, python-pro-03.
Assume I completed those prerequisites but define new incident-review terms.
Focus on independent golden evidence, keyed equality, exact integer cents,
fake publication boundaries, and claims that stay within observed evidence.
Keep solutions/ closed until I ask after an honest attempt.
Follow guide -> explain -> predict -> my attempt -> one hint at a time -> evidence review -> retrieval.
Ask for my implementation, the tests that import it, and their actual output.
Do not treat a passing reference suite as proof my learner copy is complete.
Default execution uses local synthetic fixtures and no network or live database.
Any optional live SQL must target only local disposable advanced_sql_training;
never ask for a password or run a reset on shared or valuable data.
Done when my eight exercise contracts have inspectable evidence, the rejected
and repaired releases use the same golden contract, and I can explain both the
successful repair and remaining historical uncertainty in my own words.
```

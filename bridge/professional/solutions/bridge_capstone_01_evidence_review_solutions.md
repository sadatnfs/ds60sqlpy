# BRIDGE-CAPSTONE-01: solution reasoning

Use this after attempting the [guide](../companion-guides/bridge_capstone_01_evidence_review.md)
and [learner](../lessons/bridge_capstone_01_evidence_review.py). The full
[executable reference](bridge_capstone_01_evidence_review_solution.py) supplies
imports, types, fixture paths, and the functions excerpted below. Run it from
the repository root with your course interpreter. It prints one JSON object
showing rejected incident evidence, accepted repair evidence, and a bounded
incident review. It reads only three synthetic local fixtures and writes no
file by default. The publication boundary is injected; main never calls a real
publisher or opens a database.

Run `python -m pytest -q bridge/professional/tests/test_bridge_capstone_01_evidence_review.py`
with the same interpreter for the focused reference suite. Those tests import
the reference, so they do not establish completion of an unfinished learner
copy. Preserve your own independently expected tests and actual output before
comparing implementations. The snippets share the complete reference's type
and helper definitions; they are explanatory excerpts, not separate scripts.

## Exercise solutions

### Exercise 1: Validate before losing information

```python
def normalize(rows: Sequence[ProductRow]) -> tuple[ProductRow, ...]:
    """Validate the keyed contract before sorting or comparing attributes."""
    identities: set[str] = set()
    for row in rows:
        _identity(row.invoice_id, "invoice_id")
        _amount(row.amount_cents)
        if row.invoice_id in identities:
            raise ValueError("duplicate invoice_id")
        identities.add(row.invoice_id)
    return tuple(sorted(rows, key=lambda row: row.invoice_id))


def load_product(path: Path) -> tuple[ProductRow, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("product JSON must be a list")
    rows: list[ProductRow] = []
    for item in raw:
        if not isinstance(item, dict) or set(item) != {"invoice_id", "amount_cents"}:
            raise ValueError("product row must contain exactly invoice_id and amount_cents")
        rows.append(
            ProductRow(_identity(item["invoice_id"], "invoice_id"), _amount(item["amount_cents"]))
        )
    return normalize(rows)
```

The loader first requires a JSON list and exactly the two declared fields on
 each row. Identity validation rejects blank values and outer whitespace rather
 than silently normalizing potentially different business keys. Amounts are
 nonnegative integer cents; Python bool must be rejected explicitly because it
 is an int subclass. The typed ProductRow does not itself enforce annotations
 at runtime, so normalize validates direct in-memory callers as well as files.

Uniqueness is checked before constructing a dictionary. A dictionary would
 otherwise keep one value per key and could hide either exact or conflicting
 duplicates. Sorted output supplies a deterministic presentation under exact,
 case-sensitive identity comparison. No trimming, currency conversion, or
 duplicate-winner rule is invented. Empty input is valid and returns an empty
 tuple. Golden invoice C's zero is a present amount, so it stays in the result.

**Expected:** Golden IDs are A,B,C with amounts 10000,5000,0. Malformed, Boolean, negative, fractional, extra-field and duplicate fixtures raise ValueError.

**Verify:** Run the malformed-boundary cases plus the literal GOLDEN fixture assertion in the focused test; each invalid input must fail before reconciliation.

### Exercise 2: Keep the summary claim narrow

```python
def summarize(rows: Sequence[ProductRow]) -> Summary:
    checked = normalize(rows)
    return Summary(len(checked), sum(row.amount_cents for row in checked))
```

Normalize before summarizing so an invalid keyed product does not acquire an
 apparently authoritative control total. Summary contains row_count and
 amount_total_cents. Both incident and golden inputs produce three rows and
 15,000 cents, which is the deliberately deceptive normal-looking result.
 Summation projects away identity and individual amount distribution, allowing
 two defects to cancel.

The correct conclusion is that these two summaries match. It is not that
 the invoice relations match, that the release was delivered, or that recovery
 succeeded. Retain summary checks because they detect other failure classes
 cheaply. Combine them with independent keyed diagnostics instead of replacing
 one weak proof with another. The test records both equal summaries and
 unequal literal ProductRow collections on the same input, so the claimed
 counterexample cannot accidentally become a case where the summary already
 reveals the fault. The empty collection has zero rows and a zero total.

**Expected:** Both summaries equal Summary(3,15000), yet the literal expected and incident tuples differ.

**Verify:** Inspect the test that asserts all three facts together: expected summary, actual summary, and unequal keyed inputs.

### Exercise 3: Reconcile the union of keys

```python
def reconcile(expected: Sequence[ProductRow], actual: Sequence[ProductRow]) -> Evidence:
    expected_rows, actual_rows = normalize(expected), normalize(actual)
    left = {row.invoice_id: row.amount_cents for row in expected_rows}
    right = {row.invoice_id: row.amount_cents for row in actual_rows}
    differences: list[Difference] = []
    for invoice_id in sorted(left.keys() | right.keys()):
        if invoice_id not in left:
            kind = "unexpected"
        elif invoice_id not in right:
            kind = "missing"
        elif left[invoice_id] != right[invoice_id]:
            kind = "changed"
        else:
            continue
        differences.append(
            Difference(invoice_id, left.get(invoice_id), right.get(invoice_id), kind)
        )
    return Evidence(
        summarize(expected_rows),
        summarize(actual_rows),
        canonical_digest(expected_rows),
        canonical_digest(actual_rows),
        tuple(differences),
    )


class Evidence:
    expected_summary: Summary
    actual_summary: Summary
    expected_digest: str
    actual_digest: str
    differences: tuple[Difference, ...]

    @property
    def accepted(self) -> bool:
        return not self.differences
```

Each side is independently normalized before its keyed dictionary is built.
 The union of keys covers expected-only and actual-only identities. Sorting
 that union produces deterministic diagnostics without assuming a particular
 input row order. Presence checks come before amount comparison, so missing C
 is distinct from a known amount of zero. The three categories are mutually
 exclusive for a unique identity: unexpected, missing, or changed.

Evidence contains summaries, canonical digests, and the complete difference
 tuple. The accepted property means no differences remain under this exact
 keyed contract. It does not mean a publisher was called or that a consumer
 received data. Equal empty inputs are accepted because the contract permits
 an empty product; a domain requiring at least one invoice would need another
 independently tested rule. The tests compare complete Difference records,
 including None placement, rather than only counting three diagnostic rows.

**Expected:** B changed 5000 to 4000, C missing 0 to None, and D unexpected None to 1000, in that identity order. Golden/Golden and empty/empty accept.

**Verify:** Compare exact diagnostic tuples and test a standalone zero-valued missing invoice to ensure zero is never treated as absent.

### Exercise 4: Reconstruct the complete parent relation

```python
def load_source_lines(path: Path) -> tuple[SourceLine, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("source JSON must be a list")
    rows: list[SourceLine] = []
    for item in raw:
        if not isinstance(item, dict) or set(item) != {"line_id", "invoice_id", "amount_cents"}:
            raise ValueError("source row has unexpected fields")
        rows.append(
            SourceLine(
                _identity(item["line_id"], "line_id"),
                _identity(item["invoice_id"], "invoice_id"),
                _amount(item["amount_cents"]),
            )
        )
    return tuple(rows)


def build_product(
    invoice_ids: Sequence[str], lines: Sequence[SourceLine]
) -> tuple[ProductRow, ...]:
    """Aggregate validated source lines while preserving zero-line invoices."""
    totals: dict[str, int] = {}
    for invoice_id in invoice_ids:
        checked = _identity(invoice_id, "invoice_id")
        if checked in totals:
            raise ValueError("duplicate invoice identity in manifest")
        totals[checked] = 0
    seen: set[str] = set()
    for line in lines:
        line_id = _identity(line.line_id, "line_id")
        if line_id in seen:
            raise ValueError("duplicate line_id")
        seen.add(line_id)
        invoice_id = _identity(line.invoice_id, "invoice_id")
        if invoice_id not in totals:
            raise ValueError("line references an invoice absent from the manifest")
        totals[invoice_id] += _amount(line.amount_cents)
    return normalize([ProductRow(invoice_id, amount) for invoice_id, amount in totals.items()])
```

The invoice manifest creates the complete set of parent identities before any
 line is processed. Initializing their totals to zero preserves C even though
 C has no source line. Each line must have a unique line_id, refer to an
 existing parent, and carry a valid exact amount. Duplicate line IDs are
 rejected even when their values match: the lesson has no approved replay or
 deduplication policy, so silently choosing a winner would hide uncertainty.

The transformer allocates its own dictionary and returns new immutable
 ProductRow values. It does not mutate the caller's list or the checked-in
 fixtures. Sorting happens only after aggregation. A repaired result is
 compared with the unchanged independent golden file, never with an expected
 result generated by this same function. Tests separately cover empty input,
 a zero-line parent, orphans, duplicate parents, duplicate lines, and invalid
 cents. These negative controls target information loss and overcounting,
 which a single passing total would not expose.

**Expected:** The complete repaired tuple is A=10000, B=5000, C=0. The source list remains byte-for-byte equivalent as values, and malformed line relations are rejected.

**Verify:** Use literal ProductRow expectations, a copied input list, and separate orphan/duplicate cases; do not call build_product to manufacture the expected answer.

### Exercise 5: Define bytes before computing a digest

```python
def canonical_digest(rows: Sequence[ProductRow]) -> str:
    payload = {"contract_version": 1, "rows": [asdict(row) for row in normalize(rows)]}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
```

Canonicalization explicitly includes contract_version 1 and the validated,
 identity-sorted rows. Dataclass conversion provides named fields, JSON sorts
 object keys, compact separators remove formatting variability, and ASCII-safe
 encoding plus UTF-8 defines repeatable bytes. SHA-256 then fingerprints those
 bytes. Reversing presentation order cannot change this product's digest,
 while a changed identity or amount changes the encoded content.

The fixture digest is pinned independently in the tests. That check detects
 an accidental encoding change as well as an amount change. A deliberate new
 schema or encoding needs a new contract version and reviewed fixture update;
 do not merely replace the pinned digest to silence a failing test. The hash
 supplies content identification under the encoding, not source authenticity,
 semantic correctness, or historical custody. Invalid duplicates fail before
 encoding, and the separate golden reconciliation supplies the semantic
 evidence the fingerprint alone cannot provide.

**Expected:** Golden digest is fddc2c8909fee69e1b96661b9e11a1e87c7212bfe2d5f731a9f45ed2ae868fc3; row reordering preserves it and incident amounts change it.

**Verify:** Run the pinned digest, reversed input, changed amount, and duplicate-key cases as separate controls.

### Exercise 6: Place the effect behind the gate

```python
def publish_checked(
    release_id: str,
    expected: Sequence[ProductRow],
    actual: Sequence[ProductRow],
    publisher: Publisher,
) -> Evidence:
    checked_id = _identity(release_id, "release_id")
    # Snapshot caller input once so the reviewed data and emitted data agree.
    rows = normalize(actual)
    evidence = reconcile(expected, rows)
    if not evidence.accepted:
        raise ReleaseRejected("invoice identities or amounts differ from the golden contract")
    publisher.publish(checked_id, rows, evidence.actual_digest)
    return evidence
```

The function validates release identity, snapshots and normalizes actual rows
 once, computes evidence against expected rows, and rejects mismatches before
 invoking the supplied adapter. The exact tuple used in review is passed to
 the publisher with its digest, so later mutation of the caller's list cannot
 change emitted data. The fake records the full call, making ordering and
 payload review possible without any external system.

The function performs no automatic retry. If an adapter records an effect and
 then loses its acknowledgement, an exception cannot prove that no effect
 occurred. The test fake reproduces that boundary by appending one record
 before raising. The caller receives the error and the call count remains
 one. A real system would need an idempotency and outcome-reconciliation
 contract before retrying. This reference does not claim atomicity between a
 local report, a database, and an external publisher.

**Expected:** Rejected incident produces ReleaseRejected and zero fake calls. Repaired rows produce one sorted reviewed call. Failure after recording propagates after one call.

**Verify:** Inspect the zero-call test, exact recorded payload/digest, mutable-input snapshot test, and record-then-raise negative control.

### Exercise 7: Write a review artifact without overwriting

```python
def write_evidence(evidence: Evidence, path: Path) -> None:
    """Create a deterministic review artifact without overwriting existing work."""
    payload = {"contract_version": 1, "accepted": evidence.accepted, **asdict(evidence)}
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(payload, output, sort_keys=True, indent=2, ensure_ascii=True)
        output.write("\n")
```

The writer serializes the evidence value with an explicit contract version and
 accepted verdict. Dataclass conversion preserves the ordered diagnostic list,
 including None as JSON null. Sorted keys and a final newline make the output
 deterministic and readable. The caller owns the path and decides where an
 artifact belongs; main does not create any file by default.

Opening in exclusive mode x combines creation and existence checking in the
 filesystem operation. A second attempt raises FileExistsError without
 truncating the original file. Checking exists first and then using write
 mode would introduce a race and an overwrite hazard. Exclusive creation is
 still not a transactional artifact publication protocol: a crash can leave
 a partial newly created report. Keep that limitation explicit. The focused
 test uses a temporary directory, reads the report back as JSON, checks the
 missing-zero diagnostic, and verifies that a failed overwrite leaves the
 original bytes unchanged.

**Expected:** A report contains contract_version, accepted, both summaries, both digests, and ordered differences. Rewriting the same path raises FileExistsError and preserves its bytes.

**Verify:** Round-trip the JSON and compare pre/post bytes around the rejected second write; a filename existing is not evidence of complete content.

### Exercise 8: Bound the incident narrative by evidence

```python
def incident_review(before: Evidence, after: Evidence) -> IncidentReview:
    if before.accepted or not after.accepted:
        raise ValueError("review requires rejected before evidence and accepted repair evidence")
    if before.expected_digest != after.expected_digest:
        raise ValueError("repair must use the same independent golden contract")
    summary_note = (
        "matching row count and total cents"
        if before.expected_summary == before.actual_summary
        else "different summary controls"
    )
    impact = "; ".join(
        f"{difference.invoice_id}: {difference.kind}, "
        f"expected_cents={difference.expected_cents}, actual_cents={difference.actual_cents}"
        for difference in before.differences
    )
    return IncidentReview(
        observed=f"{len(before.differences)} keyed differences exist alongside {summary_note}.",
        impact=impact,
        cause_status=(
            "Unproven: the supplied snapshots do not identify the historical defect or actor."
        ),
        repair="Rebuild from validated source lines and the complete invoice manifest.",
        verification=(
            "The repaired keyed relation matches the unchanged independent golden fixture."
        ),
        unresolved=(
            "Whether a real consumer received the incident release is unknown.",
            "The original transform and deployment timeline are not supplied.",
            "Fake publication evidence does not prove production recovery.",
        ),
    )
```

The review requires a rejected before state and accepted after state under
 the identical expected digest. That prevents a repair from passing merely
 because someone changed the golden answer. The observed statement and impact
 are derived from diagnostic evidence rather than assuming every incident has
 the fixture's particular invoice names. A mismatch can be described precisely
 without pretending to know the historical source-code defect.

Cause status remains unproven because the original transform and deployment
 timeline are absent. Repair is a verified reconstruction from supplied source
 facts; production delivery and consumer recovery remain unresolved. The
 narrative does not blame an actor or claim a live operation occurred. Tests
 reject already-accepted before states, still-rejected repairs, and a passing
 result against a different golden dataset. A useful handoff pairs this
 narrative with actual attempted code, test output, rejected evidence, and
 accepted repair evidence so another reviewer can reproduce its bounded
 conclusions.

**Expected:** The review names changed, missing, and unexpected invoices, reports causal uncertainty, and retains consumer delivery and production recovery as unknown.

**Verify:** Check same-golden rejection and both verdict boundaries, then read the note for any unsupported historical or production claim.

## Limits of the evidence

The synthetic fixture fixes the domain to one currency, nonnegative integer
cents, exact case-sensitive invoice identity, and an immutable complete parent
manifest. It does not cover multi-currency conversion, partial refunds,
authorization, database isolation, real idempotent delivery, or production
acceptance. Adding any of those requires a new explicit contract and
independent cases. A correct local repair is a meaningful result even while
the historical cause remains unknown. Do not trade that precision for a more
confident story.

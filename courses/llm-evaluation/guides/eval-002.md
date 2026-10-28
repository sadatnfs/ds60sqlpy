# eval-002: Evaluation data, grouping and contamination

## Starting point and outcome

Beginner; approximately 120 minutes. Direct prerequisites: `eval-001`.

Build a reproducible family/time split and detect identifier, near-duplicate and availability-time leakage before scoring.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-002`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## A split protects a question, not a filename

Training, development and final evaluation serve different roles. Training estimates model parameters. Development supports choices such as retrieval depth, prompt wording and abstention thresholds. Final evaluation measures the selected procedure on data not used for those choices. Moving a file to a folder called test does not erase earlier access to its labels.

Requests often share a template, source document or user history. If one variant is in training and a paraphrase is in testing, the apparent held-out result may measure template reuse rather than transfer to a new family. The correct grouping depends on the deployment claim. A new-document claim needs document separation; a future-period claim needs time ordering; a new-user claim needs user separation. These restrictions can be combined, and their combination may leave much less data than a random row split.

The fixture records decision time and label-availability time separately. A label observed on day 12 cannot be used by a training procedure deployed on day 10 even if the underlying event happened on day 8. Similarly, a retrieval document corrected after an answer was issued cannot be treated as evidence available to that historical system. Keep the corpus snapshot and its timestamp with the model and prompt versions.

## Worked case A: split complete families

The program assigns complete families to partitions and then verifies disjoint group sets. It also verifies unique request IDs. This is a construction rule for a small fixture, not a random sampling design. In a larger study, a stable keyed assignment can make splits reproducible, but a hash alone does not create representativeness or preserve temporal order.

A deliberately broken split places two rows from one family in different partitions. The validator identifies that contamination before any score is computed. It does not need to know whether a language model actually memorized the content. Separation is a property the protocol can enforce independently of a model's unknown internal behavior.

```python
import hashlib


def validate_split(rows):
    seen = set()
    groups = {}
    for row in rows:
        if row["id"] in seen:
            raise ValueError("Duplicate ID")
        seen.add(row["id"])
        prior = groups.setdefault(row["family"], row["split"])
        if prior != row["split"]:
            raise ValueError("Family leakage")
    return groups


def training_ids(rows, cutoff):
    return [r["id"] for r in rows if r["event"] <= cutoff and r["label_available"] <= cutoff]


def fingerprint(text):
    normalized = " ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def worked_a():
    rows = [
        {"id": "m1", "family": "metrics", "split": "train"},
        {"id": "m2", "family": "metrics", "split": "train"},
        {"id": "p1", "family": "policy", "split": "test"},
    ]
    assert validate_split(rows) == {"metrics": "train", "policy": "test"}
    broken = [dict(r) for r in rows]
    broken[1]["split"] = "test"
    try:
        validate_split(broken)
    except ValueError as error:
        assert str(error) == "Family leakage"
    else:
        raise AssertionError("Leaking split accepted")
    print("Family split accepted; leaking split rejected")


worked_a()
```

## Worked case B: labels available at the cutoff

The second program selects training rows only when both their events and labels were available by the chosen cutoff. A tempting alternative filters only on event time. That alternative admits a delayed label that did not exist at deployment. The code displays the difference explicitly.

A normalized-content fingerprint detects a simple duplicated question despite capitalization and surrounding whitespace. Such a detector is useful for exact or near-exact administrative duplication. It cannot prove that a benchmark is uncontaminated by a pretraining corpus. Semantic paraphrases, translations and derived answer keys require further investigation. Document the detector's scope rather than converting zero matches into a universal clean-data claim.

```python
import hashlib


def validate_split(rows):
    seen = set()
    groups = {}
    for row in rows:
        if row["id"] in seen:
            raise ValueError("Duplicate ID")
        seen.add(row["id"])
        prior = groups.setdefault(row["family"], row["split"])
        if prior != row["split"]:
            raise ValueError("Family leakage")
    return groups


def training_ids(rows, cutoff):
    return [r["id"] for r in rows if r["event"] <= cutoff and r["label_available"] <= cutoff]


def fingerprint(text):
    normalized = " ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def worked_b():
    rows = [
        {"id": "a", "event": 8, "label_available": 9},
        {"id": "b", "event": 8, "label_available": 12},
        {"id": "c", "event": 11, "label_available": 11},
    ]
    assert training_ids(rows, 10) == ["a"]
    assert [r["id"] for r in rows if r["event"] <= 10] == ["a", "b"]
    assert fingerprint("  Define  conversion RATE ") == fingerprint("define conversion rate")
    print("Training at day 10:", training_ids(rows, 10))


worked_b()
```

## Data identities and protocol access

Use separate identifiers for a request, its family, a generated answer, a label event and a dataset version. An answer ID should bind the request, model checkpoint, generation settings and actual output. A label version should bind its rubric and adjudication history. A dataset digest identifies bytes; it does not establish permission, relevance or absence of selection bias.

Keep an access ledger for development and final data. The final dataset should be opened only under the declared protocol. If its failure cases motivate new prompt or model changes, move that work back into development and acquire a new final assessment. Reusing an old test set is useful for regression testing, but its score no longer has the same untouched-test interpretation.

## Diagnosis and transfer

A suspiciously large improvement should trigger a join audit: which requests survived, which groups were split, which labels arrived late, and whether one system saw a newer corpus. Compare missing and rejected rows as first-class results. Do not silently inner-join away failed generations.

For an actual data-science assistant, preserve a manifest of document snapshots and evaluation eligibility. Redaction and access policy must happen before a retrieved context enters the model. The offline examples here check grouping, time logic and simple duplicate detection. They do not inspect any real training corpus or certify that a pretrained model has never seen the benchmark.


## Six investigations

### 1. Split paraphrases

Put two paraphrases from one family into train and test.

**Expected:** Family validation fails.

**Hint:** Group by the dependency that the deployment claim must cross.

### 2. Include cutoff equality

Use event and label times exactly equal to the cutoff.

**Expected:** The row is eligible under the stated inclusive policy.

**Hint:** Compare <= with <.

### 3. Reject a delayed label

Use event 9, label 11, cutoff 10.

**Expected:** The row is excluded.

**Hint:** Event time does not imply information availability.

### 4. Separate normalization from meaning

Compare fingerprints of rate and rates.

**Expected:** The fingerprints differ.

**Hint:** This normalizer handles case and whitespace only.

### 5. Version the retrieval corpus

Explain why a document corrected after the cutoff needs another corpus version.

**Expected:** Historical evaluation uses the earlier available version.

**Hint:** Ask what the system could have observed then.

### 6. Audit an empty partition

Create a valid group assignment with an empty test partition.

**Expected:** Grouping validation alone is insufficient for an evaluation.

**Hint:** Distinguish structural validity from adequate coverage.

## Primary references

- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [Existing group/time validation](../../../python/professional/README.md)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.

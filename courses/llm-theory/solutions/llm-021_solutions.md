# llm-021: explanatory solutions

Read these document splits and contamination controls answers after attempting *Assign a second family policy* through *Distinguish normalization policy*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Audit all partition pairs* points to one step. `llm-021_solution.py` holds the assertions; this page explains how they test exact duplicate. Then try *Distinguish normalization policy* on a fresh input you chose before looking.

## Mechanism review

Document splitting is an identity problem before it is a random-number problem. Exact content hashes identify byte-identical duplicates, while known family IDs group related paraphrases or versions that differ in bytes. Assign a family wholly to one partition, then verify both family and hash intersections. Freeze the partition manifest before evaluation and keep it available for review. Normalization choices matter: trimming or Unicode normalization can change which documents are considered identical, so declare those choices rather than applying them silently. This local authored corpus makes provenance and grouping inspectable without retrieving any external text.

**Exact duplicate:** Two documents with identical bytes under the declared policy.

**Family split:** A partition assignment shared by related documents.

**Frozen manifest:** An unchanged record of identities and their partitions.

## Reading the implementation

Hash UTF-8 text with SHA256 under a raw-text policy. Map each family to train, validation or test, then derive document assignments. Compare sets across every pair of partitions. Serialize the manifest with sorted keys for a stable identity receipt. A hash is a content fingerprint, not a claim that two different hashes represent independent documents.

## Exercise 1: Assign a second family policy

The question is: Use documents p, p2, p3 in family J, q in K and r in L; map J to test, K to train and L to validation.

Assigning whole families keeps all three related documents on the test side. The split sizes follow the family sizes, so a large family can leave very little training data.

```python
family2 = {"p": "J", "p2": "J", "p3": "J", "q": "K", "r": "L"}
policy2 = {"J": "test", "K": "train", "L": "validation"}
manifest2 = {doc: policy2[group] for doc, group in family2.items()}
assert sorted(d for d, s in manifest2.items() if s == "test") == ["p", "p2", "p3"]
assert list(manifest2.values()).count("train") == 1 and manifest2["r"] == "validation"
```

**Expected:** p, p2 and p3 all test; one training document q; r in validation.

**Verify:** For *Assign a second family policy*, a fresh-process check confirms `sorted((d for d, s in manifest2.items() if s == 'test')) == ['p', 'p2', 'p3']`; `list(manifest2.values()).count('train') == 1` and `manifest2['r'] == 'validation'`.

## Exercise 2: Predict the effect of key order

The question is: Serialize the same two-entry manifest with keys in opposite orders, with and without sort_keys=True, and compare SHA-256 hashes.

A hash identifies bytes, not meaning. A manifest hash is only a stable identity when the serialization is canonical, so the key order must be fixed before hashing.

```python
forward = json.dumps({"a": "train", "b": "test"})
backward = json.dumps({"b": "test", "a": "train"})
assert hash_text(forward) != hash_text(backward)
assert hash_text(json.dumps({"a": "train", "b": "test"}, sort_keys=True)) == hash_text(
    json.dumps({"b": "test", "a": "train"}, sort_keys=True)
)
```

**Expected:** raw JSON hashes differ when only key order changes; sort_keys=True makes them equal.

**Verify:** For *Predict the effect of key order*, a fresh-process check confirms `hash_text(forward) != hash_text(backward)` and the combined assertion.

## Exercise 3: Audit all partition pairs

The question is: Construct family sets for train, validation, test and compare pairwise intersections.

Checking only train versus test misses validation contamination, which can affect model or prompt selection before final testing.

```python
sets = {part: {family[d] for d, p in manifest.items() if p == part} for part in policy.values()}
assert (
    not sets["train"] & sets["validation"]
    and not sets["train"] & sets["test"]
    and not sets["validation"] & sets["test"]
)
```

**Expected:** all three intersections empty.

**Verify:** For *Audit all partition pairs*, a fresh-process check confirms `not sets['train'] & sets['validation']`, `not sets['train'] & sets['test']` and `not sets['validation'] & sets['test']`.

## Exercise 4: Inject a known leak

The question is: Move `a2` into validation and rerun the family intersection.

A negative control proves the audit detects the intended failure. A test suite containing only clean partitions can pass even when a checker always returns success.

```python
bad = dict(manifest)
bad["a2"] = "validation"
train = {family[d] for d, p in bad.items() if p == "train"}
valid = {family[d] for d, p in bad.items() if p == "validation"}
assert train & valid == {"F"}
```

**Expected:** train/validation intersection F.

**Verify:** For *Inject a known leak*, a fresh-process check confirms `train & valid == {'F'}`.

## Exercise 5: Preserve the manifest identity

The question is: Hash canonical manifest JSON before and after computing an evaluation summary.

Evaluation should read partition state. The digest reveals mutation but must accompany the actual manifest so a reviewer can inspect its content.

```python
payload = lambda: json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
before = hashlib.sha256(payload()).hexdigest()
summary = {"test_documents": sum(p == "test" for p in manifest.values())}
assert summary["test_documents"] == 1 and hashlib.sha256(payload()).hexdigest() == before
```

**Expected:** hash unchanged.

**Verify:** For *Preserve the manifest identity*, a fresh-process check confirms `summary['test_documents'] == 1` and `hashlib.sha256(payload()).hexdigest() == before`.

## Exercise 6: Distinguish normalization policy

The question is: Compare raw hashes for red square and red square followed by a space; compare hashes after explicit stripping.

Neither policy is universally correct. The lesson requires the policy to be stated before deduplication and splitting so identity rules cannot be tuned to a desired result.

```python
assert hash_text("red square") != hash_text("red square ")
assert hash_text("red square".strip()) == hash_text("red square ".strip())
```

**Expected:** raw hashes differ; stripped hashes match.

**Verify:** For *Distinguish normalization policy*, a fresh-process check confirms `hash_text('red square') != hash_text('red square ')` and `hash_text('red square'.strip()) == hash_text('red square '.strip())`.

## Review after comparison

Change one input to *Inject a known leak* and predict the result first; keep *Preserve the manifest identity* failing beside the repair. Log a missing NumPy separately from a wrong exact duplicate value in `llm-021`.

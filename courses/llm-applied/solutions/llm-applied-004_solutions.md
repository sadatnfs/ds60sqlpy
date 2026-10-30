# llm-applied-004: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A domain corpus is a versioned dataset. Each document needs a stable identity, source, permission basis, version, scope and content fingerprint. The same topic may have several versions, and the newest is not necessarily the version appropriate for a historical question. Retrieval should not mix contradictory versions without explaining which one applies. Evaluation isolation also operates at the document-family level: a paraphrase or revision of a test answer can leak into training or prompt selection even when its exact hash differs.

This lesson uses six authored snippets about data-science methods. One is restricted, and one contains hostile-looking instructions. Neither receives special execution power from its text. A manifest stores source metadata beside content identity. Hashing detects byte changes; it does not prove permission, semantic independence or correctness. Keep the actual source and policy record available for review. A corpus update should produce a new versioned artifact and trigger evaluation of retrieval and citation behavior before replacing a served index.

**Corpus manifest:** A record of source identities, versions and admission metadata.

**Content hash:** A fingerprint of exact bytes under a stated encoding.

**Document family:** Related versions or derivatives treated as one evaluation unit.

**Scope:** The audience or authorization class permitted to read a document.

## Reading the implementation

Canonical JSON with sorted keys makes manifest hashing stable across dictionary insertion order. SHA256 fingerprints UTF-8 text. Compare family sets across partitions and validate one active version per family under a simple current-only policy. A missing permission field is an admission failure, not an invitation to infer permission. Do not strip or normalize text before hashing unless that normalization policy is declared and separately recorded.

## Follow a corpus update through its derived artifacts

The fixture changes conversion from purchases divided by eligible visits to purchases divided by eligible accounts. Even if the same numerator is used, those denominators can differ. With three purchases, ten eligible visits and five eligible accounts, the two definitions yield0.3 and 0.6. A system using the newer text with older computation code may produce a coherent-looking answer that combines incompatible versions.

A content fingerprint detects a byte change under the chosen encoding. Here SHA256 is applied to UTF-8 text. It does not establish who wrote the text, whether it is accurate, whether its permission statement is legitimate or which date it applies to. Likewise, permission='course-fixture' is an explicit fixture value; the code does not consult a real policy owner. These distinctions are why dataset documentation should retain purpose, collection and intended-use information beside integrity metadata. [Datasheets for Datasets](https://arxiv.org/abs/1803.09010).

The admission helper checks required-key presence, a nonempty permission value and text/hash equality. It allows additional fields and does not fully validate every field's type or consult an identity provider. That is its exact local contract. A source can pass those checks and still be semantically wrong or unauthorized under an external policy. Describe such a result as integrity/metadata admission, not a complete trust determination.

The active-version loop selects the largest version value within each family. Suppose version 1 applies through January and version 2 begins in February. A question about a January experiment needs version 1 even if version 2 is current today. If version 2 was discovered in March but applies retroactively from February, effective time and ingestion time differ again. A reproducible answer needs the applicable policy and the system's evidence snapshot, not just the newest filename.

| Artifact | Parent identity that must remain traceable | Example stale mismatch |
| --- | --- | --- |
| Admitted document | Source version and exact content hash | Changed text with old hash |
| Chunk | Document version and original offsets | Old offsets applied to new text |
| Vector or lexical index | Chunk identities and encoding/tokenizer policy | Rebuilt corpus with old index |
| Cached answer | Evidence, prompt, model and effective access policy | Privileged or obsolete answer reused |

A release can prepare a new corpus and derived index together, verify their compatibility, and switch the served identity only after checks pass. The six-document fixture does not implement an atomic deployment protocol. The table states which identities a larger implementation would need to bind. Keeping an old index alive temporarily is not automatically wrong, provided the served version is explicit and its access/freshness policy still permits it.

Evaluation isolation follows semantic lineage as well as bytes. metric-v1 and metric-v2 have different hashes but share a family. A model or prompt selected using one may already have seen the task structure behind the other. Conversely, two unrelated documents can legitimately share a common boilerplate sentence. Define families using the dependence relevant to the intended generalization claim, rather than equating every shared token with leakage or every different hash with independence.

### Interview reasoning with explanatory answers

**Does a hash prove authenticity?** It detects content disagreement with a declared digest. Authenticity additionally needs a trusted association between that digest, the source identity and the publication process. A maliciously replaced text and digest can agree perfectly.

**Why version an index separately from a corpus?** Index construction can lag, fail partially or change tokenization/embedding policy without changing the original documents. The two identities describe different artifacts.

**Why is selecting the newest document insufficient?** The newest version may not apply to the event being analyzed, and conflicting sources may have different authority. Applicability and precedence must be stated before resolving a conflict.

## Exercise 1: Fingerprint authored sources

The question is: Add source=course-authored, permission=course-fixture and SHA256 to each local document.

The fixture explicitly supplies its provenance. In a real corpus those fields need evidence from the source owner or governing policy, not autogenerated guesses.

```python
manifest = [
    {
        **doc,
        "source": "course-authored",
        "permission": "course-fixture",
        "sha256": fingerprint(doc["text"]),
    }
    for doc in DOCUMENTS
]
assert len(manifest) == 6 and all(len(d["sha256"]) == 64 for d in manifest)
```

**Expected:** 6 complete records; all hashes contain 64 characters.

**Verify:** Compare the computed values or written argument with 6 complete records; all hashes contain 64 characters.

## Exercise 2: Detect a changed definition

The question is: Create metric-v2 with changed text and compare content hashes to metric-v1.

A denominator change is a semantic change, not a formatting update. Retaining both versions supports historical questions and exposes stale-index risks.

```python
old = manifest[0]
new = {
    **old,
    "id": "metric-v2",
    "version": 2,
    "text": "Conversion rate equals purchases divided by eligible accounts.",
}
new["sha256"] = fingerprint(new["text"])
assert new["sha256"] != old["sha256"] and new["family"] == old["family"] and new["version"] == 2
```

**Expected:** hash differs; family remains metric; version is2.

**Verify:** Compare the computed values or written argument with hash differs; family remains metric; version is2.

## Exercise 3: Choose an active version explicitly

The question is: Select the highest version per family from metric-v1, metric-v2 and trial-v1.

This current-only policy is simple and explicit. A historical assistant would need effective dates and a question-time policy rather than always selecting the maximum version.

```python
active = {}
for doc in [old, new, manifest[1]]:
    if doc["family"] not in active or doc["version"] > active[doc["family"]]["version"]:
        active[doc["family"]] = doc
assert {d["id"] for d in active.values()} == {"metric-v2", "trial-v1"}
```

**Expected:** active IDs metric-v2 and trial-v1.

**Verify:** Compare the computed values or written argument with active IDs metric-v2 and trial-v1.

## Exercise 4: Detect family leakage

The question is: Place metric-v1 in training and metric-v2 in testing, then compare their families.

Hash disjointness alone cannot establish evaluation independence. A revised definition can reveal the same task structure or answer family.

```python
assert {old["family"]} & {new["family"]} == {"metric"} and old["sha256"] != new["sha256"]
```

**Expected:** family intersection contains metric despite different hashes.

**Verify:** Compare the computed values or written argument with family intersection contains metric despite different hashes.

## Exercise 5: Refuse incomplete admission metadata

The question is: Remove permission from one record and validate admission.

An unresolved permission field remains unresolved. A pipeline should quarantine the record or request evidence rather than filling a plausible value.

```python
candidate = dict(manifest[0])
del candidate["permission"]
try:
    admit(candidate)
except ValueError:
    pass
else:
    raise AssertionError("unknown permission admitted")
```

**Expected:** ValueError for missing permission.

**Verify:** Compare the computed values or written argument with ValueError for missing permission.

## Exercise 6: Keep instruction-like documents inert

The question is: Inspect attack-v1 and confirm its text does not alter the manifest validator or access metadata.

Content admission and instruction authority are separate. A document can be retained as adversarial test data without being allowed to change access rules.

```python
attack = next(d for d in manifest if d["id"] == "attack-v1")
private = next(d for d in manifest if d["id"] == "private-v1")
assert "Ignore" in attack["text"] and private["scope"] == "restricted"
admit(attack)
assert private["scope"] == "restricted"
```

**Expected:** attack text remains data; restricted record remains restricted.

**Verify:** Compare the computed values or written argument with attack text remains data; restricted record remains restricted.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

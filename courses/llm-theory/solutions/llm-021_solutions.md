# llm-021: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Document splitting is an identity problem before it is a random-number problem. Exact content hashes identify byte-identical duplicates, while known family IDs group related paraphrases or versions that differ in bytes. Assign a family wholly to one partition, then verify both family and hash intersections. Freeze the partition manifest before evaluation and keep it available for review. Normalization choices matter: trimming or Unicode normalization can change which documents are considered identical, so declare those choices rather than applying them silently. This local authored corpus makes provenance and grouping inspectable without retrieving any external text.

**Exact duplicate:** Two documents with identical bytes under the declared policy.

**Family split:** A partition assignment shared by related documents.

**Frozen manifest:** An unchanged record of identities and their partitions.

## Reading the implementation

Hash UTF-8 text with SHA256 under a raw-text policy. Map each family to train,validation or test, then derive document assignments. Compare sets across every pair of partitions. Serialize the manifest with sorted keys for a stable identity receipt. A hash is a content fingerprint, not a claim that two different hashes represent independent documents.

## Exercise 1: Fingerprint exact text

The question is: Hash two identical snippets and one paraphrase in the same family.

The paraphrase remains related despite a different hash. This is why content hashing and family metadata address different contamination mechanisms.

```python
import hashlib,json
hash_text=lambda t:hashlib.sha256(t.encode('utf-8')).hexdigest()
a=hash_text('red square'); copy=hash_text('red square'); para=hash_text('square colored red')
assert a==copy and a!=para
```

**Expected:** identical texts share a hash; paraphrase differs.

**Verify:** Compare the computed values or written argument with identical texts share a hash; paraphrase differs.

## Exercise 2: Assign whole families

The question is: Use documentsa,a2 inF andb inG,c inH; mapF train,G validation,H test.

The assignment is made once per family. Sampling rows independently would permit related versions to cross the boundary.

```python
family={'a':'F','a2':'F','b':'G','c':'H'}; policy={'F':'train','G':'validation','H':'test'}
manifest={doc:policy[group] for doc,group in family.items()}
assert manifest=={'a':'train','a2':'train','b':'validation','c':'test'}
```

**Expected:** a and a2 both train.

**Verify:** Compare the computed values or written argument with a and a2 both train.

## Exercise 3: Audit all partition pairs

The question is: Construct family sets for train,validation,test and compare pairwise intersections.

Checking only train versus test misses validation contamination, which can affect model or prompt selection before final testing.

```python
sets={part:{family[d] for d,p in manifest.items() if p==part} for part in policy.values()}
assert not sets['train']&sets['validation'] and not sets['train']&sets['test'] and not sets['validation']&sets['test']
```

**Expected:** all three intersections empty.

**Verify:** Compare the computed values or written argument with all three intersections empty.

## Exercise 4: Inject a known leak

The question is: Movea2 into validation and rerun the family intersection.

A negative control proves the audit detects the intended failure. A test suite containing only clean partitions can pass even when a checker always returns success.

```python
bad=dict(manifest); bad['a2']='validation'
train={family[d] for d,p in bad.items() if p=='train'}; valid={family[d] for d,p in bad.items() if p=='validation'}
assert train&valid=={'F'}
```

**Expected:** train/validation intersectionF.

**Verify:** Compare the computed values or written argument with train/validation intersectionF.

## Exercise 5: Preserve the manifest identity

The question is: Hash canonical manifest JSON before and after computing an evaluation summary.

Evaluation should read partition state. The digest reveals mutation but must accompany the actual manifest so a reviewer can inspect its content.

```python
payload=lambda:json.dumps(manifest,sort_keys=True,separators=(',',':')).encode(); before=hashlib.sha256(payload()).hexdigest()
summary={'test_documents':sum(p=='test' for p in manifest.values())}
assert summary['test_documents']==1 and hashlib.sha256(payload()).hexdigest()==before
```

**Expected:** hash unchanged.

**Verify:** Compare the computed values or written argument with hash unchanged.

## Exercise 6: Distinguish normalization policy

The question is: Compare raw hashes for red square and red square followed by a space; compare hashes after explicit stripping.

Neither policy is universally correct. The lesson requires the policy to be stated before deduplication and splitting so identity rules cannot be tuned to a desired result.

```python
assert hash_text('red square')!=hash_text('red square ')
assert hash_text('red square'.strip())==hash_text('red square '.strip())
```

**Expected:** raw hashes differ; stripped hashes match.

**Verify:** Compare the computed values or written argument with raw hashes differ; stripped hashes match.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

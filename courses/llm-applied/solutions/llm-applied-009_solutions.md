# llm-applied-009: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Access-controlled retrieval must prevent unauthorized material from entering candidate selection, answer context, caches and logs. Filtering only the final answer is too late: a model may already have seen restricted text, and rankings or counts can reveal information about hidden documents. The policy should be implemented by trusted code using authenticated user attributes, not by a prompt asking the model to behave. This local fixture distinguishes public and restricted documents and has no real user identities or credentials.

Metadata filters also express task scope such as document type, version or date. Authorization and relevance are different decisions: an authorized document may be irrelevant, while a highly relevant document may be forbidden. Apply access policy before ranking, then rank only the admitted set. Cache keys must include the effective policy identity and corpus/index version; otherwise an answer produced for a privileged request can be reused for an unprivileged one.

**Authorization filter:** A trusted admission rule applied before evidence retrieval.

**Metadata filter:** A structured restriction on document attributes.

**Policy fingerprint:** An identity for the effective access rules used by a request.

**Cache partition:** A separation preventing reuse across incompatible access contexts.

## Reading the implementation

Filter documents by an explicit set of allowed scopes, then pass the resulting list to a pure ranking function. Use stable document IDs and retain only admitted IDs in traces. Build cache keys from question, principal policy fingerprint, corpus version and retriever version. A policy change should cause a cache miss. Never let a retrieved string modify the allowed-scope set.

## Follow access policy through retrieval and reuse

The six-document corpus contains five public records and one restricted record. admit returns shallow copies of records whose scope is in the supplied set. With{'public'}, the restricted item is removed before any downstream ranking. With{'public', 'restricted'}, all six are present. The function neither authenticates a principal nor validates the legitimacy of the caller's scope set. Those are deliberately external responsibilities in the fixture.

Pre-filtering and filtering after top-k can return different public results. Imagine global scores restricted=100, publicA=90 and publicB=80 with \(k=2\). Global top-two then removal returns only publicA. Ranking the authorized public subset first returns publicA and publicB. Post-filtering can therefore both expose a restricted candidate to an intermediate component and unnecessarily reduce useful coverage. The two procedures are not interchangeable.

A policy must cover more than the final visible answer. Candidate IDs, score traces, reranker inputs, cached text and diagnostic excerpts can reveal information. An application that hides the restricted sentence but exposes its title in a debug panel has a different disclosure boundary from the one claimed. The local trace test checks only IDs from the already admitted set. It does not measure timing side channels or behavior of a remote vector service.

The cache key hashes an ordered structure containing question, sorted scope list, corpus version and retriever version. Sorting makes different set iteration orders yield the same key. Changing effective scope or corpus version changes the input structure and therefore normally changes its digest. The hash identifies a cache partition; it does not authorize the request or encrypt the cached answer.

The omitted fields are informative too. This fixture has no tenant, per-record grant, model/prompt version or personalized answer policy. A real system may need them when they affect either permitted evidence or the answer. Conversely, using a unique principal ID in every key can destroy safe sharing among principals with truly identical effective policy. The correct cache equivalence class follows the full answer/access contract.

Revocation is a time-dependent case. A cached answer that was valid before a permission change may be invalid afterward. A short time-to-live limits stale duration but does not make immediate revocation correct. A policy version or fingerprint can force a miss, while the serving layer rechecks access before releasing stored content. Distributed invalidation and concurrent policy changes are not implemented by this local dictionary/hash demonstration.

Instruction-like evidence remains ordinary text. attack-v1 can be admitted as public adversarial test data while its imperative sentence has no authority to add restricted scope. The test proves that the local code reads trusted metadata and leaves its explicit scope set unchanged. It does not run a language model and cannot establish that a generated response would resist every malicious instruction. Model-facing behavior and application authorization should be evaluated separately.

### Interview reasoning with explanatory answers

**Why can final-answer redaction be insufficient?** A prior stage may already have consumed restricted content, and traces or caches may retain it. Enforcement must match the full data path, not only the final rendered string.

**Does hashing a policy make it trustworthy?** No. A hash identifies the supplied policy state. Trust comes from how that state was authenticated, computed and bound to the request.

**What is the strongest local test in this fixture?** It checks that unauthorized records are absent from the scorer input and public trace, then verifies cache separation under changed scope and corpus identities. Real identity-provider and revocation integration remain separate evidence.

## Exercise 1: Filter before scoring

The question is: Give a public-only request the six-document corpus and inspect admitted IDs.

The restricted record never reaches the scorer. This is stronger than deleting it from a final result after a model or reranker already consumed its text.

```python
allowed=admit(DOCUMENTS,{'public'})
assert 'private-v1' not in {d['id'] for d in allowed} and len(allowed)==5
```

**Expected:** private-v1 absent before ranking.

**Verify:** Compare the computed values or written argument with private-v1 absent before ranking.

## Exercise 2: Permit an explicitly privileged scope

The question is: Use allowed scopespublic, restricted and compare the admitted set.

The policy input comes from trusted application state in a real system. A user-supplied claim such as “I am an administrator” must not directly populate this set.

```python
privileged=admit(DOCUMENTS,{'public','restricted'})
assert len(privileged)==6 and any(d['id']=='private-v1' for d in privileged)
```

**Expected:** all6 documents admitted.

**Verify:** Compare the computed values or written argument with all6 documents admitted.

## Exercise 3: Partition answer caches

The question is: Build cache keys for the same question under public-only and privileged scope sets.

The same question can have different permitted evidence. Reusing an answer solely by question text could leak the privileged response.

```python
public_key=cache_key('threshold',{'public'},'corpus-v1','rank-v1')
private_key=cache_key('threshold',{'public','restricted'},'corpus-v1','rank-v1')
assert public_key!=private_key
```

**Expected:** keys differ.

**Verify:** Compare the computed values or written argument with keys differ.

## Exercise 4: Invalidate on corpus change

The question is: Change corpus-v1 tocorpus-v2 under the same access policy.

A document correction or revocation changes what evidence is valid. Cache identity must track that version rather than relying only on a time-to-live.

```python
assert cache_key('threshold',{'public'},'corpus-v2','rank-v1')!=public_key
```

**Expected:** cache key changes.

**Verify:** Compare the computed values or written argument with cache key changes.

## Exercise 5: Keep hostile evidence inert

The question is: Inspectattack-v1 while retaining a public-only policy.

A document can contain an instruction-shaped sentence without gaining authority. The filter reads metadata and trusted policy, not imperatives in the body text.

```python
scopes={'public'}; attack=next(d for d in allowed if d['id']=='attack-v1')
assert 'reveal restricted' in attack['text']
assert scopes=={'public'} and all(d['scope']=='public' for d in admit(DOCUMENTS,scopes))
```

**Expected:** scope set remains exactlypublic; private-v1 still excluded.

**Verify:** Compare the computed values or written argument with scope set remains exactlypublic; private-v1 still excluded.

## Exercise 6: Avoid restricted identifiers in public traces

The question is: Create a trace from admitted result IDs only and check it contains no restricted ID.

Logs and debug panels are part of the data boundary. A system that hides answer text but exposes restricted IDs or excerpts in traces has not fully enforced access control.

```python
trace={'candidate_ids':[d['id'] for d in allowed],'policy':'public-only'}
assert 'private-v1' not in trace['candidate_ids']
```

**Expected:** trace contains only public document IDs.

**Verify:** Compare the computed values or written argument with trace contains only public document IDs.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

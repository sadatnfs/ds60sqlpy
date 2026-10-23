# llm-028: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A tiny-transformer capstone combines model mechanics, fitting and evaluation into one inspectable experiment. The training corpus is local and authored, the vocabulary is fixed, and document families define the split. The decoder has fewer than fifty thousand parameters and uses at most thirty-two context positions. A fixed small update budget prevents unbounded experimentation. Compare held-out token loss with a train-only count baseline using the same vocabulary and target events. Model hashes and split hashes record identity, while causal tests and denominator checks establish different properties. A poor score or an inconclusive comparison is a valid result when its limitations are reported honestly.

**Capstone evidence:** A combined record of mechanics, data lineage and held-out observations.

**Count baseline:** A smoothed transition model fitted on the same training data.

**Frozen test:** Assessment data excluded from model and prompt selection.

## Reading the implementation

Use the provided TinyDecoder with seed11. Train on shifted local sequences for exactly20 updates. Count bigram transitions without crossing document boundaries, apply add-one smoothing and evaluate the same held-out pairs. Hash canonical integer sequences and detached model parameter bytes separately. Open the heldout split only after freezing the update budget and model choice.

## Exercise 1: Freeze corpus identity

The question is: Use train sequences[1,2,3,4],[1,2,4,3] and holdout[1,3,2,4] with distinct document IDs.

The literal corpus prevents hidden downloads and makes every target visible. Document identity is separate from token identity because repeated tokens are expected across splits.

```python
import hashlib,json
docs=[[1,2,3,4],[1,2,4,3]]; held=[1,3,2,4]; split={'train':['a','b'],'test':['c']}; digest=hashlib.sha256(json.dumps(split,sort_keys=True).encode()).hexdigest()
assert len(docs)==2 and len(held)-1==3 and len(digest)==64
```

**Expected:** train2 documents;holdout1;context3.

**Verify:** Compare the computed values or written argument with train2 documents;holdout1;context3.

## Exercise 2: Train a bounded decoder

The question is: Initialize seed11 and train20 Adam(.01) updates on the two training sequences.

The budget and architecture are fixed before held-out evaluation. Training loss is retained as diagnostic evidence rather than a substitute for a test score.

```python
torch.manual_seed(11); model=TinyDecoder(); opt=torch.optim.Adam(model.parameters(),lr=.01); batch=torch.tensor(docs); curve=[]
for _ in range(20):
    opt.zero_grad(set_to_none=True); logits,_=model(batch[:,:-1]); loss=F.cross_entropy(logits.reshape(-1,16),batch[:,1:].reshape(-1)); loss.backward(); opt.step(); curve.append(loss.item())
assert len(curve)==20 and np.isfinite(curve).all() and sum(p.numel() for p in model.parameters())<50000
```

**Expected:** 20 finite losses;parameter count below50000.

**Verify:** Compare the computed values or written argument with 20 finite losses;parameter count below50000.

## Exercise 3: Fit the count baseline

The question is: Build16x16 transition counts from training documents and add-one smooth each row.

The baseline uses the same vocabulary as the neural model. Changing vocabulary size would change the smoothing denominator and make the comparison less direct.

```python
counts=np.zeros((16,16))
for doc in docs:
    for a,b in zip(doc[:-1],doc[1:]): counts[a,b]+=1
prob=(counts+1)/(counts.sum(1,keepdims=True)+16)
assert counts.sum()==6; np.testing.assert_allclose(prob.sum(1),1,atol=1e-12,rtol=0)
```

**Expected:** total6 observed transitions; every row sums1.

**Verify:** Compare the computed values or written argument with total6 observed transitions; every row sums1.

## Exercise 4: Score one frozen holdout

The question is: Compute both mean losses on the three held-out target events.

The lesson does not promise that a tiny trained transformer beats the count model. The observed comparison is the result, including when it is unfavorable.

```python
model.eval(); sequence=torch.tensor([held])
with torch.no_grad(): z,_=model(sequence[:,:-1]); neural=F.cross_entropy(z.reshape(-1,16),sequence[:,1:].reshape(-1)).item()
baseline=-np.mean([np.log(prob[a,b]) for a,b in zip(held[:-1],held[1:])])
assert np.isfinite([neural,baseline]).all() and len(held)-1==3
```

**Expected:** both finite; denominator3; no required winner.

**Verify:** Compare the computed values or written argument with both finite; denominator3; no required winner.

## Exercise 5: Retest causality after training

The question is: Compare the first two logits from the full holdout input with an independent two-token prefix.

Training should not weaken the architecture information boundary. Testing after updates also guards against accidental changes to evaluation code.

```python
with torch.no_grad():
    full,_=model(sequence[:,:-1]); prefix,_=model(sequence[:,:2])
torch.testing.assert_close(prefix,full[:,:2],atol=1e-6,rtol=0)
```

**Expected:** prefix agreement within1e-6.

**Verify:** Compare the computed values or written argument with prefix agreement within1e-6.

## Exercise 6: Record model identity and limits

The question is: Hash ordered parameter bytes and build a report with3 held-out targets,20 updates and the split hash.

Hashes identify this run state but do not prove the experiment is valid. The report must retain the actual split and failure analysis alongside those fingerprints.

```python
model_hash=hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in model.parameters())).hexdigest()
report={'model_hash':model_hash,'split_hash':digest,'updates':20,'targets':3,'neural_loss':neural,'baseline_loss':float(baseline),'limit':'One authored held-out document.'}
assert len(model_hash)==64 and report['targets']==3 and report['updates']==20
```

**Expected:** two64-character hashes and explicit tiny-corpus limitation.

**Verify:** Compare the computed values or written argument with two64-character hashes and explicit tiny-corpus limitation.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

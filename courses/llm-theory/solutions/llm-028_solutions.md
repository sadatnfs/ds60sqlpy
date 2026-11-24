# llm-028: explanatory solutions

Read these capstone: train and audit a tiny transformer answers after attempting *Freeze corpus identity* through *Record model identity and limits*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Fit the count baseline* points to one step. `llm-028_solution.py` holds the assertions; this page explains how they test capstone evidence. Then try *Record model identity and limits* on a fresh input you chose before looking.

## Mechanism review

A tiny-transformer capstone combines model mechanics, fitting and evaluation into one inspectable experiment. The training corpus is local and authored, the vocabulary is fixed, and document families define the split. The decoder has fewer than fifty thousand parameters and uses at most thirty-two context positions. A fixed small update budget prevents unbounded experimentation. Compare held-out token loss with a train-only count baseline using the same vocabulary and target events. Model hashes and split hashes record identity, while causal tests and denominator checks establish different properties. A poor score or an inconclusive comparison is a valid result when its limitations are reported honestly.

**Capstone evidence:** A combined record of mechanics, data lineage and held-out observations.

**Count baseline:** A smoothed transition model fitted on the same training data.

**Frozen test:** Assessment data excluded from model and prompt selection.

## Reading the implementation

Use the provided TinyDecoder with seed 11. Train on shifted local sequences for exactly 20 updates. Count bigram transitions without crossing document boundaries, apply add-one smoothing and evaluate the same held-out pairs. Hash canonical integer sequences and detached model parameter bytes separately. Open the heldout split only after freezing the update budget and model choice.

## Exercise 1: Freeze corpus identity

The question is: Use train sequences [1, 2, 3, 4], [1, 2, 4, 3] and holdout [1, 3, 2, 4] with distinct document IDs.

The literal corpus prevents hidden downloads and makes every target visible. Document identity is separate from token identity because repeated tokens are expected across splits.

```python
import hashlib, json

docs = [[1, 2, 3, 4], [1, 2, 4, 3]]
held = [1, 3, 2, 4]
split = {"train": ["a", "b"], "test": ["c"]}
digest = hashlib.sha256(json.dumps(split, sort_keys=True).encode()).hexdigest()
assert len(docs) == 2 and len(held) - 1 == 3 and len(digest) == 64
```

**Expected:** train 2 documents; holdout 1; context 3.

**Verify:** For *Freeze corpus identity*, a fresh-process check confirms `len(docs) == 2`, `len(held) - 1 == 3` and `len(digest) == 64`.

## Exercise 2: Train a bounded decoder

The question is: Initialize seed 11 and train 20 Adam(0.01) updates on the two training sequences.

The budget and architecture are fixed before held-out evaluation. Training loss is retained as diagnostic evidence rather than a substitute for a test score.

```python
torch.manual_seed(11)
model = TinyDecoder()
opt = torch.optim.Adam(model.parameters(), lr=0.01)
batch = torch.tensor(docs)
curve = []
for _ in range(20):
    opt.zero_grad(set_to_none=True)
    logits, _ = model(batch[:, :-1])
    loss = F.cross_entropy(logits.reshape(-1, 16), batch[:, 1:].reshape(-1))
    loss.backward()
    opt.step()
    curve.append(loss.item())
assert (
    len(curve) == 20
    and np.isfinite(curve).all()
    and sum(p.numel() for p in model.parameters()) < 50000
)
```

**Expected:** 20 finite losses; parameter count below 50000.

**Verify:** For *Train a bounded decoder*, a fresh-process check confirms `len(curve) == 20`, `np.isfinite(curve).all()` and `sum((p.numel() for p in model.parameters())) < 50000`.

## Exercise 3: Fit the count baseline

The question is: Build 16x16 transition counts from training documents and add-one smooth each row.

The baseline uses the same vocabulary as the neural model. Changing vocabulary size would change the smoothing denominator and make the comparison less direct.

```python
counts = np.zeros((16, 16))
for doc in docs:
    for a, b in zip(doc[:-1], doc[1:]):
        counts[a, b] += 1
prob = (counts + 1) / (counts.sum(1, keepdims=True) + 16)
assert counts.sum() == 6
np.testing.assert_allclose(prob.sum(1), 1, atol=1e-12, rtol=0)
```

**Expected:** total 6 observed transitions; every row sums 1.

**Verify:** For *Fit the count baseline*, a fresh-process check confirms `counts.sum() == 6` and `prob.sum(1)` matches `1` within 1e-12.

## Exercise 4: Score one frozen holdout

The question is: Compute both mean losses on the three held-out target events.

The lesson does not promise that a tiny trained transformer beats the count model. The observed comparison is the result, including when it is unfavorable.

```python
model.eval()
sequence = torch.tensor([held])
with torch.no_grad():
    z, _ = model(sequence[:, :-1])
    neural = F.cross_entropy(z.reshape(-1, 16), sequence[:, 1:].reshape(-1)).item()
baseline = -np.mean([np.log(prob[a, b]) for a, b in zip(held[:-1], held[1:])])
assert np.isfinite([neural, baseline]).all() and len(held) - 1 == 3
```

**Expected:** both finite; denominator 3; no required winner.

**Verify:** For *Score one frozen holdout*, a fresh-process check confirms `np.isfinite([neural, baseline]).all()` and `len(held) - 1 == 3`.

## Exercise 5: Retest causality after training

The question is: Compare the first two logits from the full holdout input with an independent two-token prefix.

Training should not weaken the architecture information boundary. Testing after updates also guards against accidental changes to evaluation code.

```python
with torch.no_grad():
    full, _ = model(sequence[:, :-1])
    prefix, _ = model(sequence[:, :2])
torch.testing.assert_close(prefix, full[:, :2], atol=1e-6, rtol=0)
```

**Expected:** prefix agreement within 1e-6.

**Verify:** For *Retest causality after training*, a fresh-process check confirms `prefix` matches `full[:, :2]` within 1e-6.

## Exercise 6: Record model identity and limits

The question is: Hash ordered parameter bytes and build a report with 3 held-out targets, 20 updates and the split hash.

Hashes identify this run state but do not prove the experiment is valid. The report must retain the actual split and failure analysis alongside those fingerprints.

```python
model_hash = hashlib.sha256(
    b"".join(p.detach().numpy().tobytes() for p in model.parameters())
).hexdigest()
report = {
    "model_hash": model_hash,
    "split_hash": digest,
    "updates": 20,
    "targets": 3,
    "neural_loss": neural,
    "baseline_loss": float(baseline),
    "limit": "One authored held-out document.",
}
assert len(model_hash) == 64 and report["targets"] == 3 and report["updates"] == 20
```

**Expected:** two 64-character hashes and explicit tiny-corpus limitation.

**Verify:** For *Record model identity and limits*, a fresh-process check confirms `len(model_hash) == 64`, `report['targets'] == 3` and `report['updates'] == 20`.

## Review after comparison

Change one input to *Score one frozen holdout* and predict the result first; keep *Retest causality after training* failing beside the repair. Log a missing PyTorch separately from a wrong capstone evidence value in `llm-028`.

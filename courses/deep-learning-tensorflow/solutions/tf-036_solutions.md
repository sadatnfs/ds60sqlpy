# tf-036: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A model release is a decision backed by a bundle of evidence. It needs a prediction contract, frozen preprocessing, the identity of fitting and assessment records, and a recoverable artifact. A hash can detect accidental changes to bytes, but cannot establish that those bytes contain a good model or honest data split. A release gate combines independent checks and blocks when a required one fails. The tiny linear model is intentionally transparent so the lesson can concentrate on packaging and decision logic. A no-go is a valid capstone result. Production rollout, privacy guarantees and broad reliability remain outside this offline teaching exercise.

**Release gate:** A conjunction of required checks that permits or blocks a decision.

**Lineage:** The identities of data, preprocessing and artifacts used.

**Rollback artifact:** A retained previous version that can restore a known state.

## Reading the implementation

Serialize metadata with sorted keys and fixed separators before hashing. Keep schema, weights and split IDs in separate fields so a reviewer can identify what changed. Run prediction parity on fixed probes and reject a schema mismatch before inference. The checkpoint parity proof from tf-028 and export proof from tf-032 are distinct evidence items; neither should be replaced by a boolean invented without execution.

## Exercise 1: Build a literal model bundle

The question is: Create a float32 two-feature model with coefficient[2,-1] and schema width2.

A known probe connects the serialized feature order to numerical behavior. Swapping features would change the prediction even if the model file remained readable.

```python
weights=np.array([[2.],[-1.]],dtype='float32'); schema={'features':['a','b'],'dtype':'float32','width':2}
model=tf.keras.Sequential([tf.keras.Input(shape=(2,)),tf.keras.layers.Dense(1,use_bias=False)]); model.layers[0].set_weights([weights])
np.testing.assert_array_equal(model(np.array([[3,4]],dtype='float32')).numpy(),[[2]])
```

**Expected:** probe[3,4] predicts2.

**Verify:** Compare the computed values or written argument with probe[3,4] predicts2.

## Exercise 2: Freeze and hash a split manifest

The question is: Hash train IDs[a,b] and test IDs[c,d] using canonical JSON.

The canonical representation avoids a digest change caused only by dictionary key order. The explicit intersection check verifies a property that a hash alone cannot establish.

```python
import hashlib,json
split={'train':['a','b'],'test':['c','d']}; payload=json.dumps(split,sort_keys=True,separators=(',',':')).encode(); digest=hashlib.sha256(payload).hexdigest()
assert not set(split['train'])&set(split['test']) and len(digest)==64
```

**Expected:** disjoint IDs and a64-character SHA256.

**Verify:** Compare the computed values or written argument with disjoint IDs and a64-character SHA256.

## Exercise 3: Catch tampered lineage

The question is: Change one test ID and compare the resulting digest.

This control proves the check is sensitive to the field that matters. It does not authenticate an author or replace a trusted distribution mechanism.

```python
changed={'train':['a','b'],'test':['c','e']}; other=hashlib.sha256(json.dumps(changed,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert other!=digest
```

**Expected:** digest differs.

**Verify:** Compare the computed values or written argument with digest differs.

## Exercise 4: Block incompatible schemas

The question is: Compare an incoming three-feature schema with the frozen two-feature schema before prediction.

A model might accept a tensor through unintended broadcasting or fail later with a low-level error. A named schema gate explains the problem before executing the wrong interpretation.

```python
incoming={'features':['a','b','c'],'dtype':'float32','width':3}
assert incoming!=schema
```

**Expected:** schema gate isFalse.

**Verify:** Compare the computed values or written argument with schema gate isFalse.

## Exercise 5: Make the decision fail closed

The question is: Evaluate required gates with an unexecuted restart proof represented asNone, then with an actual failed schema gate.

Unknown evidence is not a pass. The lesson deliberately avoids fabricating a restart receipt and shows that even three passing checks cannot compensate for a required failed fourth check.

```python
gates={'prediction':True,'split':True,'restart':None,'schema':True}
assert not all(value is True for value in gates.values())
gates.update(restart=True,schema=False); assert not all(value is True for value in gates.values())
```

**Expected:** both decisionsno-go.

**Verify:** Compare the computed values or written argument with both decisionsno-go.

## Exercise 6: Retain a rollback decision

The question is: Construct a release record with previous artifact ID, holdout count and limits; keep no-go when any gate fails.

A release record should explain what can be restored and why a candidate was blocked. A failed capstone check is useful evidence, not an invitation to bypass the gate.

```python
record={'candidate':'v2','previous':'v1','holdout_count':2,'decision':'go' if all(v is True for v in gates.values()) else 'no-go','limits':['synthetic fixture only']}
assert record['decision']=='no-go' and record['previous']=='v1' and record['holdout_count']==2
```

**Expected:** decisionno-go and previous artifactv1 retained.

**Verify:** Compare the computed values or written argument with decisionno-go and previous artifactv1 retained.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

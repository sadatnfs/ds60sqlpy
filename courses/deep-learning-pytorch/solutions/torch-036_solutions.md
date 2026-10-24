# torch-036: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A reproducible model release is a bundle of state, schema, data identity, execution evidence and limitations. A valid artifact must reconstruct the intended model and produce checked predictions in a fresh process. A hash detects changed bytes but does not prove that the bytes contain a useful or honestly evaluated model. Release gates should fail on missing or incorrect evidence rather than silently treat unknown checks as passed.

This capstone trains a small scalar regressor under a fixed budget, saves its state with a feature/dtype schema and split manifest, and executes a fresh-process inference check. It then deliberately corrupts the declared state hash and proves that the loader rejects the bundle before using it. The temporary release is a local teaching artifact, not a deployment. The final record distinguishes local contract acceptance from unestablished production reliability and retains a rollback identity.

**Release bundle:** The model state, semantic schema, lineage and evidence needed for reconstruction.

**Integrity gate:** A check that artifact bytes match their recorded identity.

**Fresh-process inference:** Prediction after reconstruction without live parent objects.

**Rollback identity:** A retained previous artifact reference used in a recovery decision.

## Reading the implementation

Train an nn.Linear(1, 1, bias=False) on literal float64 points using fixed SGD updates. Serialize state_dict, canonical JSON schema and split IDs into an owned Temporary Directory. Record SHA256 of the weight file. The child verifies the hash and schema before constructing the module and loading weights_only=True. Bound the subprocess, include stderr on unexpected failure, and remove only the owned temporary directory.

## Connect the trained function to the released bytes

The training objective is \(L(w)=\frac{14}{3}(w-2)^2\) on x=[1, 2, 3]. With learning rate 0.01, the error \(e_{t}=w_{t}-2\) follows \(e_{t+1}=\frac{68}{75}e_t\). Starting at zero gives \(w_t=2-2\left(\frac{68}{75}\right)^t\). After the fixed thirty updates, the analytic weight is approximately 1.89420638. This derivation supplies an independent check on the training mechanism rather than relying only on the loop's finite-value assertion.

The held-out inputs are 4 and 5, with targets 8 and 10. The training-mean target baseline predicts four, so its squared errors are 16 and 36 and MSE is 26. For the trained scalar model, the holdout MSE is \(\frac{16+25}{2}(w_{30}-2)^2=82\left(\frac{68}{75}\right)^{60}\), approximately 0.229442. The threshold below 26 is therefore interpretable for this visible fixture. It does not establish population quality: the rule y=2x is public, and both assessment inputs extrapolate beyond the training range.

The predictor is more than its state tensor. Its architecture is bias-free Linear(1, 1), its dtype is float64, its feature list is['x'], and its output represents the same scalar target units. The manifest carries that schema, split IDs, step count and a digest of the serialized weight file. A future normalized or categorical model would also need its fitted preprocessing and label mapping. Reconstructing a tensor of the right shape cannot recover omitted semantic metadata.

The digest binds the manifest's expected weight identity to the actual saved bytes. The child recomputes SHA256 before loading and rejects a mismatch. The deliberate all-zero expected digest exercises that rejection path. It is a successful negative test because the invalid bundle fails with the expected diagnostic; it does not mean the corrupted bundle is an accepted release.

Integrity is narrower than authenticity or correctness. A digest does not identify a trusted publisher by itself, and a party able to replace both weights and the expected digest can create a different self-consistent pair. Correctly hashed bytes can also encode a poor model or dishonest split. The lesson's local artifacts are trusted teaching inputs, so it tests byte mismatch detection rather than a signed distribution or supply-chain system.

The child separately checks the exact schema before constructing the model. That catches a changed feature/dtype/width contract even if the weight bytes are unchanged. The current child does not independently revalidate every possible lineage field or reproduce training. The parent established disjoint split IDs earlier, and the manifest records them; those facts should not be inflated into authenticated data lineage or are computed training receipt.

Fresh-process prediction parity removes the possibility of satisfying the test by reusing the original model object. The child loads the saved state with weights_only=True on CPU, sets evaluation mode, and predicts the two fixed rows under inference_mode. The parent compares with its recorded outputs at 1e-12 for this float64 fixture. That is a local inference-reconstruction proof, not an optimizer/RNG continuation proof. The earlier checkpoint and export lessons are separate evidence items rather than booleans to assume here.

A useful gate table keeps these distinctions explicit:

| Gate | Evidence in this capstone | Limit |
| --- | --- | --- |
| training procedure | thirty actual updates and analytic fixture | no unseen-population claim |
| weight integrity | recomputed digest and deliberate mismatch rejection | no publisher authentication |
| schema | exact child-side dictionary comparison | no general semantic-schema validator |
| reconstruction | fresh child predictions agree | not training continuation |
| assessment | two visible held-out rows and baseline | very limited coverage |
| rollback | previous identity v1 recorded | no previous artifact restored here |
| operations | not exercised | production remains no-go |

The previous-artifact string is a decision reference, not proof that a recoverable file exists or that it is compatible with current preprocessing. A real rollback rehearsal would load the identified previous artifact, verify its schema and predictions, and define the effect on any surrounding state. This exercise retains the reference without claiming that rehearsal occurred.

Publication and cleanup also have boundaries. The files are created in one owned TemporaryDirectory and removed after the checks. No server, registry or deployment is started. A completed save/load test does not establish crash-safe publication, concurrent-reader behavior or long-term retention. Those require their own artifact lifecycle and operational tests.

The final record can therefore say local_contracts_pass=True and production_go=False without contradiction. It acknowledges successful mechanics while preserving missing assessment and operational evidence. The paired TensorFlow release uses different formats and some different gates, but follows the same principle: each claim should be supported by the corresponding actual check, and a required unknown or failure must remain visible.

## Exercise 1: Freeze the scalar experiment

The question is: Use train x = [1, 2, 3] and holdout 4, 5 with target 2 x and disjoint IDs.

The data identity is fixed before training. The tiny holdout is useful for local mechanics but not sufficient for a broad quality claim.

```python
x=torch.tensor([[1.],[2.],[3.]],dtype=torch.float64); y=2*x; held=torch.tensor([[4.],[5.]],dtype=torch.float64)
split={'train':['a','b','c'],'test':['d','e']}; assert not set(split['train'])&set(split['test']) and len(split['test'])==2
```

**Expected:** 3 training and 2 holdout records.

**Verify:** Compare the computed values or written argument with 3 training and 2 holdout records.

## Exercise 2: Train within a declared budget

The question is: Zero-initialize float64 Linear and run 30 SGD.01 updates.

The budget is not extended after seeing the holdout. The baseline predicts training mean target 4, so gives errors 16 and 36on the two test rows.

```python
model=nn.Linear(1,1,bias=False,dtype=torch.float64)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.01)
for _ in range(30):
    optimizer.zero_grad(set_to_none=True); (model(x)-y).square().mean().backward(); optimizer.step()
model.eval()
with torch.no_grad(): expected=model(held); error=(expected-2*held).square().mean().item()
assert torch.isfinite(model.weight).all() and error<26
```

**Expected:** finite weights; holdout error below constant training-mean baseline 26.

**Verify:** Compare the computed values or written argument with finite weights; holdout error below constant training-mean baseline 26.

## Exercise 3: Build the owned release bundle

The question is: Save weights, schema and split manifest with a weight SHA256.

The hash binds the manifest to the saved bytes. The feature order and dtype provide semantic information that a state dictionary alone cannot explain.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); weights=folder/'weights.pt'; torch.save(model.state_dict(),weights)
manifest={'schema':{'features':['x'],'dtype':'float64','width':1},'split':split,'weight_sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'steps':30}
manifest_path=folder/'manifest.json'; manifest_path.write_text(json.dumps(manifest,sort_keys=True))
assert len(manifest['weight_sha256'])==64 and manifest['schema']['width']==1
```

**Expected:** manifest has feature x, float64, width 1 and matching hash.

**Verify:** Compare the computed values or written argument with manifest has feature x, float64, width 1 and matching hash.

## Exercise 4: Verify fresh-process prediction parity

The question is: Run the checked loader in a fresh interpreter and compare holdout predictions.

The child reconstructs from files and cannot reuse the trained parent module. The integrity and schema gates execute before loading state.

```python
child=textwrap.dedent("""
import hashlib,json,sys,torch
from pathlib import Path
from torch import nn
folder=Path(sys.argv[1]); manifest=json.loads((folder/'manifest.json').read_text()); weights=folder/'weights.pt'
if hashlib.sha256(weights.read_bytes()).hexdigest()!=manifest['weight_sha256']: raise ValueError('weight hash mismatch')
if manifest['schema']!={'features':['x'],'dtype':'float64','width':1}: raise ValueError('schema mismatch')
model=nn.Linear(1,1,bias=False,dtype=torch.float64); model.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True)); model.eval()
with torch.inference_mode(): predictions=model(torch.tensor([[4.],[5.]],dtype=torch.float64)).tolist()
print(json.dumps(predictions))
""")
compile(child,'torch-release-child','exec')
result=subprocess.run([sys.executable,'-c',child,str(folder)],capture_output=True,text=True,timeout=60,check=False)
if result.returncode: raise RuntimeError('release child failed: '+result.stderr)
np.testing.assert_allclose(json.loads(result.stdout.strip().splitlines()[-1]),expected.numpy(),atol=1e-12,rtol=0)
```

**Expected:** predictions match within 1e-12.

**Verify:** Compare the computed values or written argument with predictions match within 1e-12.

## Exercise 5: Make a corrupted artifact fail

The question is: Replace the declared weight hash with 64 zeros and rerun the loader.

A negative control proves the gate can actually block a bad bundle. A file-existence check would not detect this identity mismatch.

```python
broken={**manifest,'weight_sha256':'0'*64}; manifest_path.write_text(json.dumps(broken,sort_keys=True))
rejected=subprocess.run([sys.executable,'-c',child,str(folder)],capture_output=True,text=True,timeout=60,check=False)
assert rejected.returncode!=0 and 'weight hash mismatch' in rejected.stderr
manifest_path.write_text(json.dumps(manifest,sort_keys=True))
```

**Expected:** nonzero child exit and weight hash mismatch diagnostic.

**Verify:** Compare the computed values or written argument with nonzero child exit and weight hash mismatch diagnostic.

## Exercise 6: Record a bounded decision and cleanup

The question is: Record local parity pass, holdout count 2, previous artifact v1 and production no-go, then remove owned files.

The local acceptance is real but limited. A production decision needs representative data, operational boundaries and additional reliability evidence; the capstone does not invent them.

```python
receipt={'local_contracts_pass':True,'test_count':2,'previous_artifact':'v1','production_go':False,'limits':['synthetic fixture','no operational deployment test']}
temporary.cleanup()
assert receipt['local_contracts_pass'] and not receipt['production_go'] and not folder.exists()
```

**Expected:** local checks True; production no-go; directory absent.

**Verify:** Compare the computed values or written argument with local checks True; production no-go; directory absent.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

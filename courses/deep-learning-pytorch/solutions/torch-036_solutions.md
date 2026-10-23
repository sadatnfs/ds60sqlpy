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

Train ann.Linear(1, 1, bias=False) on literal float64 points using fixed SGD updates. Serialize state_dict, canonical JSON schema and split IDs into an owned Temporary Directory. Record SHA256 of the weight file. The child verifies the hash and schema before constructing the module and loading weights_only=True. Bound the subprocess, include stderr on unexpected failure, and remove only the owned temporary directory.

## Exercise 1: Freeze the scalar experiment

The question is: Use train x1, 2, 3 and holdout4, 5 with target2 x and disjoint IDs.

The data identity is fixed before training. The tiny holdout is useful for local mechanics but not sufficient for a broad quality claim.

```python
x=torch.tensor([[1.],[2.],[3.]],dtype=torch.float64); y=2*x; held=torch.tensor([[4.],[5.]],dtype=torch.float64)
split={'train':['a','b','c'],'test':['d','e']}; assert not set(split['train'])&set(split['test']) and len(split['test'])==2
```

**Expected:** 3 training and2 holdout records.

**Verify:** Compare the computed values or written argument with 3 training and2 holdout records.

## Exercise 2: Train within a declared budget

The question is: Zero-initialize float64 Linear and run30 SGD.01 updates.

The budget is not extended after seeing the holdout. The baseline predicts training mean target4, so gives errors16 and36 on the two test rows.

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

**Expected:** finite weights; holdout error below constant training-mean baseline26.

**Verify:** Compare the computed values or written argument with finite weights; holdout error below constant training-mean baseline26.

## Exercise 3: Build the owned release bundle

The question is: Save weights, schema and split manifest with a weight SHA256.

The hash binds the manifest to the saved bytes. The feature order and dtype provide semantic information that a state dictionary alone cannot explain.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); weights=folder/'weights.pt'; torch.save(model.state_dict(),weights)
manifest={'schema':{'features':['x'],'dtype':'float64','width':1},'split':split,'weight_sha256':hashlib.sha256(weights.read_bytes()).hexdigest(),'steps':30}
manifest_path=folder/'manifest.json'; manifest_path.write_text(json.dumps(manifest,sort_keys=True))
assert len(manifest['weight_sha256'])==64 and manifest['schema']['width']==1
```

**Expected:** manifest has feature x, float64, width1 and matching hash.

**Verify:** Compare the computed values or written argument with manifest has feature x, float64, width1 and matching hash.

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

**Expected:** predictions match within1e-12.

**Verify:** Compare the computed values or written argument with predictions match within1e-12.

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

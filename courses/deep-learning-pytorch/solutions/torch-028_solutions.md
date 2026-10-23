# torch-028: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Restartable training requires the state that determines the next update, not merely weights that reproduce the current prediction. Adam stores moment estimates and a step counter. Random draws can affect the next batch or target perturbation. Data position determines which observation comes next. A checkpoint contract must name all of these components and define what is fixed or restored. A weights-only restart can match immediate predictions while taking a different subsequent step.

This lesson saves a small linear model, Adam state, CPU RNG state and an explicit data-position counter after two updates. It compares an uninterrupted next draw and update with a fresh interpreter restoring the trusted local checkpoint. The literal batch is fixed; this does not claim to restore a multiprocessing DataLoader or a distributed sampler. Temporary artifacts are owned and removed by the lesson. Float32 comparisons use a declared tolerance rather than promising cross-platform bitwise identity.

**Training checkpoint:** State sufficient for a declared continuation contract.

**RNG state:** The position of a pseudorandom generator used by future operations.

**Data position:** The declared next point in the training input sequence.

**Next-step parity:** Agreement after one identical restored and uninterrupted update.

## Reading the implementation

Save a dictionary of model.state_dict, optimizer.state_dict, torch.get_rng_state and simple metadata. Reconstruct fresh objects before load_state_dict, and restore RNG after object construction so initialization draws do not advance the restored stream. torch.load uses weights_only=True for this trusted tensor-and-primitive checkpoint. The child program is dedented, compiled before launch, bounded by a timeout, and includes stderr in a failure.

## Exercise 1: Create nontrivial training state

The question is: Take two Adam updates of a zero-weight linear model onx1, 2 andy2 x.

Saving before any updates would not test nonzero optimizer moments. Two steps create history that a fresh optimizer lacks.

```python
torch.manual_seed(7); model,optimizer=make_state()
for _ in range(2): step(model,optimizer,torch.zeros((2,1)))
parameter=next(model.parameters()); assert optimizer.state[parameter]['step'].item()==2 and parameter.item()>0
```

**Expected:** optimizer step2 and positive weight.

**Verify:** Compare the computed values or written argument with optimizer step2 and positive weight.

## Exercise 2: Save the complete local contract

The question is: Write model, optimizer, RNG and data_position2 into an owned temporary checkpoint.

The state dictionary values are serialized at this point. The checkpoint is local and trusted; the example does not load arbitrary external pick led objects.

```python
temporary=tempfile.TemporaryDirectory(); folder=Path(temporary.name); path=folder/'checkpoint.pt'
checkpoint={'model':model.state_dict(),'optimizer':optimizer.state_dict(),'rng':torch.get_rng_state(),'data_position':2}
torch.save(checkpoint,path); assert path.is_file() and checkpoint['data_position']==2
```

**Expected:** file exists and metadata position2.

**Verify:** Compare the computed values or written argument with file exists and metadata position2.

## Exercise 3: Record uninterrupted continuation

The question is: Draw three random values, then a small target perturbation, and perform the third update.

The order of random draws is part of the continuation contract. Restoring only the seed without the consumed generator state would not reproduce this point.

```python
probe=torch.rand(3); noise=torch.rand((2,1))*.01; step(model,optimizer,noise); expected=parameter.item()
assert torch.isfinite(probe).all() and optimizer.state[parameter]['step'].item()==3 and np.isfinite(expected)
```

**Expected:** finite weight, step3, and saved three-value random probe.

**Verify:** Compare the computed values or written argument with finite weight, step3, and saved three-value random probe.

## Exercise 4: Restore in a fresh interpreter

The question is: Recreate model and Adam, restore all state, repeat the same draws and update.

A new process cannot accidentally reuse the parent's optimizer or generator. The check therefore exercises reconstruction from the saved artifact.

```python
program=textwrap.dedent("""
import json,sys,torch
from torch import nn
state=torch.load(sys.argv[1],map_location='cpu',weights_only=True)
model=nn.Linear(1,1,bias=False); optimizer=torch.optim.Adam(model.parameters(),lr=.05)
model.load_state_dict(state['model']); optimizer.load_state_dict(state['optimizer']); torch.set_rng_state(state['rng'])
probe=torch.rand(3); noise=torch.rand((2,1))*.01; x=torch.tensor([[1.],[2.]]); y=2*x+noise
optimizer.zero_grad(set_to_none=True); (model(x)-y).square().mean().backward(); optimizer.step()
print(json.dumps({'probe':probe.tolist(),'weight':model.weight.item(),'position':state['data_position']+1}))
""")
compile(program,'torch-checkpoint-child','exec')
result=subprocess.run([sys.executable,'-c',program,str(path)],capture_output=True,text=True,timeout=60,check=False)
if result.returncode: raise RuntimeError('checkpoint child failed: '+result.stderr)
restored=json.loads(result.stdout.strip().splitlines()[-1])
np.testing.assert_allclose(restored['probe'],probe.tolist(),atol=0,rtol=0)
np.testing.assert_allclose(restored['weight'],expected,atol=1e-6,rtol=0); assert restored['position']==3
```

**Expected:** probe matches and next weight agrees within1e-6; position3.

**Verify:** Compare the computed values or written argument with probe matches and next weight agrees within1e-6; position3.

## Exercise 5: Expose a weights-only restart

The question is: Restore only the saved model into fresh Adam and take the same third batch update.

The immediate model function matches the saved state, but Adam's moments and counter differ. Prediction parity is weaker than training-resumption parity.

```python
state=torch.load(path,map_location='cpu',weights_only=True); weights_only,fresh_optimizer=make_state(); weights_only.load_state_dict(state['model'])
step(weights_only,fresh_optimizer,noise)
assert abs(weights_only.weight.item()-expected)>1e-6
```

**Expected:** next weight differs from full-state continuation.

**Verify:** Compare the computed values or written argument with next weight differs from full-state continuation.

## Exercise 6: Verify cleanup and bounded claims

The question is: Remove the owned checkpoint directory and report that the literal CPU batch contract was tested.

A real training system must additionally preserve sampler, worker and external-data state appropriate to its architecture. This fixture names that boundary rather than implying it was tested.

```python
temporary.cleanup(); assert not folder.exists()
receipt={'cpu_next_step_checked':True,'multiprocess_loader_restored':False,'distributed_restart_verified':False}
assert receipt['cpu_next_step_checked'] and not receipt['distributed_restart_verified']
```

**Expected:** directory absent; no distributed-loader claim.

**Verify:** Compare the computed values or written argument with directory absent; no distributed-loader claim.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

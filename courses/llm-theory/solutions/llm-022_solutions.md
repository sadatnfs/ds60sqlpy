# llm-022: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Reproducibility has several layers: a saved seed, deterministic evaluation behavior, stable data identity and sufficient training state for restart. model.eval disables dropout and changes other mode-dependent layers, but it does not disable gradient tracking; no_grad is a separate context. Adam continuation requires model parameters and optimizer state, including moments and update counters. A new-process next-step comparison is stronger than reloading weights into an object that still holds the original optimizer. This tiny scalar fixture tests restart mechanics, while the decoder prefix check tests evaluation behavior. Cross-platform bitwise identity is not promised.

**Evaluation mode:** Module behavior chosen by eval, separate from gradient recording.

**Optimizer checkpoint:** State needed to reproduce a subsequent optimization update.

**Next-step parity:** Agreement after one identical update from saved state.

## Reading the implementation

Use torch.save on a dictionary containing model state and optimizer state. Load only the locally created trusted checkpoint with weights_only=True. Reconstruct fresh objects before load_state_dict. A subprocess takes the same next step and returns its weight as JSON. A seed controls initial random draws but is not a substitute for restoring the exact optimizer state.

## Exercise 1: Create Adam history

The question is: Take two float32 Adam updates of(w-2)² fromw0.

The checkpoint must contain nontrivial history. Saving before the first update would not distinguish a full optimizer restore from a fresh optimizer.

```python
w=nn.Parameter(torch.tensor(0.)); opt=torch.optim.Adam([w],lr=.1)
for _ in range(2): opt.zero_grad(set_to_none=True); (w-2).square().backward(); opt.step()
assert w.item()>0 and opt.state[w]['step'].item()==2
```

**Expected:** positive weight and optimizer step2.

**Verify:** Compare the computed values or written argument with positive weight and optimizer step2.

## Exercise 2: Save a trusted local checkpoint

The question is: Write the scalar weight and optimizer state into an owned temporary file.

The file is created by this lesson and loaded only for this local test. Loading arbitrary untrusted serialized objects is outside the fixture.

```python
temporary=tempfile.TemporaryDirectory(); path=Path(temporary.name)/'state.pt'
torch.save({'weight':w.detach().clone(),'optimizer':opt.state_dict()},path)
assert path.is_file(); saved=w.item()
```

**Expected:** checkpoint file exists.

**Verify:** Compare the computed values or written argument with checkpoint file exists.

## Exercise 3: Calculate the uninterrupted next step

The question is: Take one more update and save the expected weight.

The control uses the same objective and optimizer settings. A different batch or learning-rate schedule would make the comparison uninterpretable.

```python
opt.zero_grad(set_to_none=True); (w-2).square().backward(); opt.step(); expected=w.item()
assert opt.state[w]['step'].item()==3 and expected!=saved
```

**Expected:** step3 and changed weight.

**Verify:** Compare the computed values or written argument with step3 and changed weight.

## Exercise 4: Restore in a new interpreter

The question is: Load the trusted checkpoint into fresh weight and Adam objects, then take one step.

The child has no live parent optimizer. Agreement therefore depends on reconstructing saved state, rather than on an accidental in-memory reference.

```python
program="""import torch,json,sys
from torch import nn
state=torch.load(sys.argv[1],map_location='cpu',weights_only=True)
w=nn.Parameter(state['weight'].clone()); opt=torch.optim.Adam([w],lr=.1); opt.load_state_dict(state['optimizer'])
opt.zero_grad(set_to_none=True); (w-2).square().backward(); opt.step()
print(json.dumps({'weight':w.item()}))
"""
result=subprocess.run([sys.executable,'-c',program,str(path)],check=True,capture_output=True,text=True,timeout=60)
restored=json.loads(result.stdout.strip().splitlines()[-1]); np.testing.assert_allclose(restored['weight'],expected,atol=1e-6,rtol=0)
```

**Expected:** child weight agrees within1e-6.

**Verify:** Compare the computed values or written argument with child weight agrees within1e-6.

## Exercise 5: Expose weights-only continuation

The question is: Initialize a fresh optimizer at the saved weight and compare its next update.

The weight alone gives the same immediate scalar prediction but a different future training trajectory. Prediction parity and restart parity are distinct tests.

```python
fresh_w=nn.Parameter(torch.tensor(saved)); fresh_opt=torch.optim.Adam([fresh_w],lr=.1)
(fresh_w-2).square().backward(); fresh_opt.step(); assert abs(fresh_w.item()-expected)>1e-6
```

**Expected:** weight differs from full-state continuation.

**Verify:** Compare the computed values or written argument with weight differs from full-state continuation.

## Exercise 6: Verify evaluation and cleanup

The question is: Use Dropout(.5) in eval mode on ones and remove only the owned temporary checkpoint.

Evaluation mode disables this stochastic layer. Cleanup is confined to the temporary fixture and never deletes learner checkpoints or progress.

```python
drop=nn.Dropout(.5); drop.eval(); ones=torch.ones(8)
assert torch.equal(drop(ones),ones); temporary.cleanup(); assert not path.exists()
```

**Expected:** dropout returns ones; temporary path absent.

**Verify:** Compare the computed values or written argument with dropout returns ones; temporary path absent.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

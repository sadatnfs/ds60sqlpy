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

## Reconstruct the next state transition, not just the current prediction

Training state is the input to a transition. A useful inventory separates components by how they influence the next step:

| Component | Role in this fixture | What weights alone omit |
| --- | --- | --- |
| model tensors | current scalar predictor | current value if absent |
| Adam moments and step | update direction/normalization | history-dependent next update |
| optimizer group options | rate and optimizer configuration | the intended update policy |
| CPU RNG state | next probe and target-noise draws | position in the random stream |
| data_position=2 | declared completed-update marker | progress metadata |
| literal x and target rule | fixed next-batch construction | a reproducible input contract |

Adam maintains \(m_t=\beta_1m_{t-1}+(1-\beta_1)g_t\) and \(v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\), then uses step-dependent bias correction and an epsilon-stabilized normalized update. Two models with identical weights but different m, v, t need not take the same next step. Saving after two real updates makes those histories nontrivial; checkpointing before any update would leave a much weaker test.

The weights-only negative control is deliberately given the same next noise tensor as the uninterrupted run. Its different result therefore isolates missing optimizer history rather than simultaneously changing the batch and the optimizer. It is a stronger experiment than comparing two restarted jobs whose data order and RNG streams are also unknown. The paired TensorFlow chapter tests the same reconstruction principle, although its scalar objective and optimizer rate differ from this PyTorch fixture; their literal weights are not a cross-framework equality oracle.

The RNG timeline has an easily missed construction step. torch.manual_seed(7) sets an initial stream. Creating nn.Linear consumes initialization randomness even though the code subsequently overwrites its weight with zero. The two initial updates use zero noise and no further random draws. The saved RNG state therefore represents a particular position after construction, not simply the number 7. The uninterrupted path next draws a three-value probe, then a2×1 noise tensor, and then updates.

The child reconstructs the model and optimizer, loads their saved state, and only then restores torch RNG state. Restoring before constructing Linear would let initialization consume a draw from the restored stream. Setting the seed again would return to the stream's beginning instead of its saved position. Matching the three-value probe checks this ordering directly before the weight comparison tests the next noisy update. [PyTorch 2.9 reproducibility guidance](https://docs.pytorch.org/docs/2.9/notes/randomness.html).

Other randomness is absent from this particular continuation. Python random, NumPy Generator objects, DataLoader generators, worker processes and accelerator generators would need their own explicit treatment if used. A global torch seed does not automatically serialize every library's current generator state. Likewise, a data_position integer does not restore a real iterator here: the next batch is always constructed from literal x=[1, 2]. Incrementing the marker to three proves the stated bookkeeping, not worker-prefetch or distributed-sampler recovery.

State dictionaries also have ownership semantics. model.state_dict() provides references to model state tensors; holding that mapping in memory is not an immutable copy while later updates mutate the model. The example immediately serializes the mapping before continuation, so the file preserves that point. For an in-memory before/after comparison, clone the values; for a restore comparison, reload the completed saved file rather than assuming a still-live dictionary remained unchanged.

Reconstruct the same architecture and optimizer parameter-group structure before loading. Optimizer state is associated with the supplied parameter groups and their ordering; similar tensor shapes do not prove the state was attached to the intended semantic parameter after an architecture edit. A scheduler, gradient scaler, EMA model or accumulated-but-not-yet-stepped gradients would add more continuation state when present. None is silently claimed restored by this small Adam example.

weights_only=True restricts the object forms used by the local tensor-and-primitive checkpoint loader. It is not a publisher-authentication mechanism or a complete resource/shape validation policy for arbitrary outside files. map_location='cpu' establishes the intended device boundary. The child process uses the existing interpreter, has a timeout and exposes stderr on failure, so a failed reconstruction is not replaced by expected output text.

Finally, the tested boundary is a completed torch.save followed by a fresh-process load. It does not inject a crash halfway through writing or prove power-loss durability. A persistent production checkpoint needs its own staged-publication, integrity and retention procedure. The local directory is owned and disposable, and the successful test removes it. Next-step parity is valuable evidence for this exact transition and environment, not a promise of bitwise agreement across versions, hardware or nondeterministic pipelines.

## Exercise 1: Create nontrivial training state

The question is: Take two Adam updates of a zero-weight linear model onx 1, 2 and y 2 x.

Saving before any updates would not test nonzero optimizer moments. Two steps create history that a fresh optimizer lacks.

```python
torch.manual_seed(7)
model, optimizer = make_state()
for _ in range(2):
    step(model, optimizer, torch.zeros((2, 1)))
parameter = next(model.parameters())
assert optimizer.state[parameter]["step"].item() == 2 and parameter.item() > 0
```

**Expected:** optimizer step 2 and positive weight.

**Verify:** Compare the computed values or written argument with optimizer step 2 and positive weight.

## Exercise 2: Save the complete local contract

The question is: Write model, optimizer, RNG and data_position2 into an owned temporary checkpoint.

The state dictionary values are serialized at this point. The checkpoint is local and trusted; the example does not load arbitrary external pick led objects.

```python
temporary = tempfile.TemporaryDirectory()
folder = Path(temporary.name)
path = folder / "checkpoint.pt"
checkpoint = {
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "rng": torch.get_rng_state(),
    "data_position": 2,
}
torch.save(checkpoint, path)
assert path.is_file() and checkpoint["data_position"] == 2
```

**Expected:** file exists and metadata position 2.

**Verify:** Compare the computed values or written argument with file exists and metadata position 2.

## Exercise 3: Record uninterrupted continuation

The question is: Draw three random values, then a small target perturbation, and perform the third update.

The order of random draws is part of the continuation contract. Restoring only the seed without the consumed generator state would not reproduce this point.

```python
probe = torch.rand(3)
noise = torch.rand((2, 1)) * 0.01
step(model, optimizer, noise)
expected = parameter.item()
assert (
    torch.isfinite(probe).all()
    and optimizer.state[parameter]["step"].item() == 3
    and np.isfinite(expected)
)
```

**Expected:** finite weight, step 3, and saved three-value random probe.

**Verify:** Compare the computed values or written argument with finite weight, step 3, and saved three-value random probe.

## Exercise 4: Restore in a fresh interpreter

The question is: Recreate model and Adam, restore all state, repeat the same draws and update.

A new process cannot accidentally reuse the parent's optimizer or generator. The check therefore exercises reconstruction from the saved artifact.

```python
program = textwrap.dedent("""
import json,sys,torch
from torch import nn
state=torch.load(sys.argv[1],map_location='cpu',weights_only=True)
model=nn.Linear(1,1,bias=False); optimizer=torch.optim.Adam(model.parameters(),lr=.05)
model.load_state_dict(state['model']); optimizer.load_state_dict(state['optimizer']); torch.set_rng_state(state['rng'])
probe=torch.rand(3); noise=torch.rand((2,1))*.01; x=torch.tensor([[1.],[2.]]); y=2*x+noise
optimizer.zero_grad(set_to_none=True); (model(x)-y).square().mean().backward(); optimizer.step()
print(json.dumps({'probe':probe.tolist(),'weight':model.weight.item(),'position':state['data_position']+1}))
""")
compile(program, "torch-checkpoint-child", "exec")
result = subprocess.run(
    [sys.executable, "-c", program, str(path)],
    capture_output=True,
    text=True,
    timeout=60,
    check=False,
)
if result.returncode:
    raise RuntimeError("checkpoint child failed: " + result.stderr)
restored = json.loads(result.stdout.strip().splitlines()[-1])
np.testing.assert_allclose(restored["probe"], probe.tolist(), atol=0, rtol=0)
np.testing.assert_allclose(restored["weight"], expected, atol=1e-6, rtol=0)
assert restored["position"] == 3
```

**Expected:** probe matches and next weight agrees within 1e-6; position 3.

**Verify:** Compare the computed values or written argument with probe matches and next weight agrees within 1e-6; position 3.

## Exercise 5: Expose a weights-only restart

The question is: Restore only the saved model into fresh Adam and take the same third batch update.

The immediate model function matches the saved state, but Adam's moments and counter differ. Prediction parity is weaker than training-resumption parity.

```python
state = torch.load(path, map_location="cpu", weights_only=True)
weights_only, fresh_optimizer = make_state()
weights_only.load_state_dict(state["model"])
step(weights_only, fresh_optimizer, noise)
assert abs(weights_only.weight.item() - expected) > 1e-6
```

**Expected:** next weight differs from full-state continuation.

**Verify:** Compare the computed values or written argument with next weight differs from full-state continuation.

## Exercise 6: Verify cleanup and bounded claims

The question is: Remove the owned checkpoint directory and report that the literal CPU batch contract was tested.

A real training system must additionally preserve sampler, worker and external-data state appropriate to its architecture. This fixture names that boundary rather than implying it was tested.

```python
temporary.cleanup()
assert not folder.exists()
receipt = {
    "cpu_next_step_checked": True,
    "multiprocess_loader_restored": False,
    "distributed_restart_verified": False,
}
assert receipt["cpu_next_step_checked"] and not receipt["distributed_restart_verified"]
```

**Expected:** directory absent; no distributed-loader claim.

**Verify:** Compare the computed values or written argument with directory absent; no distributed-loader claim.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

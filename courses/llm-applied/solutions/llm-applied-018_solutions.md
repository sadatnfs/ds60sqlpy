# llm-applied-018: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A fair adaptation comparison starts both candidates from the same base state and uses the same training examples, target masks and held-out tasks. Full SFT can change every parameter; an output-head LoRA adapter changes only a constrained set. Different trainable counts are expected, but they do not by themselves establish quality, speed or memory superiority. Keep optimization budgets and learning-rate policies explicit, and avoid selecting a winner from training loss alone.

This chapter trains two real tiny decoders on the same literal answer task. One updates the whole model; the other freezes the base and adds rank 2 adaptation to its vocabulary output projection. That placement is intentionally narrow and is not claimed to match a production LoRA configuration across attention and feed-forward modules. Both run20 updates. We compare held-out losses without requiring a particular winner, verify frozen-base bytes and prove that an unmodified adapter initially preserves base predictions. A useful result includes limitations and failure cases, not only a ranking.

**Controlled adaptation comparison:** Candidates sharing base state,data and evaluation contract.

**Target module:** The specific layer receiving an adapter update.

**Frozen-state proof:** Exact comparison of parameters required to remain unchanged.

**Task transfer metric:** Held-out behavior measured after adaptation under a fixed rubric.

## Reading the implementation

Create one base model, copy itsstate_dict into two new instances, and snapshot the initial logits. Freeze every parameter in the adapter candidate before replacing its output projection withLoRAHead. Optimize onlyparameters withrequires_gradTrue. Keep the full and adapter optimizers separate. Evaluate both with the same held-out labels underno_grad. The output head has input width32 and vocabulary16, so rank 2 adds96 trainable entries.

## Exercise 1: Clone one base into two candidates

The question is: Create a seed 31 decoder and copy its state into full and adapted candidates.

Independent model objects prevent one optimizer from changing the other candidate. Equal initial state is stronger than merely reusing the same architecture name.

```python
torch.manual_seed(31); base=TinyDecoder(); full=TinyDecoder(); adapted=TinyDecoder(); full.load_state_dict(base.state_dict()); adapted.load_state_dict(base.state_dict())
assert all(torch.equal(a,b) for a,b in zip(full.parameters(),adapted.parameters()))
```

**Expected:** all initial base parameters equal.

**Verify:** Compare the computed values or written argument with all initial base parameters equal.

## Exercise 2: Install an output-head adapter

The question is: Freeze the adapted model, replace its output layer withrank2LoRA, and compare initial logits.

ZeroB preserves the original function. The trainable count follows32*2+2*16, which is specific to this output-head placement.

```python
for p in adapted.parameters(): p.requires_grad_(False)
adapted.output=LoRAHead(adapted.output,rank=2,alpha=2)
sequence=torch.tensor([[1,2,5,3],[1,4,6,3]]); inputs=sequence[:,:-1]; labels=sequence[:,1:].clone(); labels[:,0]=-100
assert sum(p.numel() for p in adapted.parameters() if p.requires_grad)==96
with torch.no_grad():
    a,_=base(inputs); b,_=adapted(inputs); torch.testing.assert_close(a,b,atol=1e-6,rtol=0)
```

**Expected:** 96 trainable adapter entries; initial logits match base.

**Verify:** Compare the computed values or written argument with 96 trainable adapter entries; initial logits match base.

## Exercise 3: Train both candidates under fixed budgets

The question is: Run20 full-SFT updates at.01 and20 adapter updates at.03 on the same masked batch.

The rates are declared fixture settings, not tuned on the holdout. Equal step counts do not imply equal compute or equal optimization difficulty, so resource claims require measurement.

```python
frozen={name:p.detach().clone() for name,p in adapted.named_parameters() if not p.requires_grad}; curves={}
for name,model,rate in [('full',full,.01),('adapter',adapted,.03)]:
    opt=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=rate); curve=[]
    for _ in range(20):
        opt.zero_grad(set_to_none=True); loss=objective(model,inputs,labels); curve.append(loss.item()); loss.backward(); opt.step()
    curves[name]=curve
    assert np.isfinite(curve).all() and curve[-1]<curve[0]
```

**Expected:** both training losses decrease; all logged values finite.

**Verify:** Compare the computed values or written argument with both training losses decrease; all logged values finite.

## Exercise 4: Prove base preservation

The question is: Compare every frozen adapted-model parameter against its saved copy.

The check covers embeddings, attention, feed-forward and the base output weight. Inspecting onlyrequires_grad flags would miss an accidental explicit assignment.

```python
assert all(torch.equal(parameter.detach(),frozen[name]) for name,parameter in adapted.named_parameters() if not parameter.requires_grad)
```

**Expected:** all frozen tensors exactly equal.

**Verify:** Compare the computed values or written argument with all frozen tensors exactly equal.

## Exercise 5: Compare a frozen held-out task

The question is: Evaluate prompt[7, 2] withanswer[5, 3] for both candidates using the same mask.

A held-out comparison is an observation, not a test that must favor the adapter. One literal prompt remains too little evidence for a broad domain-assistant decision.

```python
held=torch.tensor([[7,2,5,3]]); held_labels=held[:,1:].clone(); held_labels[:,0]=-100; results={}
for name,model in [('full',full),('adapter',adapted)]:
    model.eval()
    with torch.no_grad(): results[name]=objective(model,held[:,:-1],held_labels).item()
assert set(results)=={'full','adapter'} and np.isfinite(list(results.values())).all()
```

**Expected:** two finite held-out losses; no predetermined winner.

**Verify:** Compare the computed values or written argument with two finite held-out losses; no predetermined winner.

## Exercise 6: Record comparison limits

The question is: Build a report with trainable counts, update budgets, target module and task scope.

The report makes the comparison reproducible and prevents a parameter-count result from being overstated as universal quality or memory evidence.

```python
report={'adapter_trainable':96,'full_trainable':sum(p.numel() for p in full.parameters()),'steps':{'full':20,'adapter':20},'target_module':'output projection only','scope':'literal-token teaching task','heldout':results}
assert report['full_trainable']>report['adapter_trainable'] and report['steps']=={'full':20,'adapter':20}
```

**Expected:** adapter96 entries; 20 updates each; scope literal-token task.

**Verify:** Compare the computed values or written argument with adapter96 entries; 20 updates each; scope literal-token task.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

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

Create one base model, copy itsstate_dict into two new instances, and snapshot the initial logits. Freeze every parameter in the adapter candidate before replacing its output projection with LoRAHead. Optimize only parameters withrequires_gradTrue. Keep the full and adapter optimizers separate. Evaluate both with the same held-out labels underno_grad. The output head has input width32 and vocabulary16, so rank 2 adds96 trainable entries.

## Trace the two candidate models from one base

The full candidate starts with 10464 trainable parameters from the decoder ledger. The adapter candidate retains those base values frozen and adds A[32, 2] and B[2, 16] to the output projection, for64+32=96 trainable entries. The trainable ratio is96/10464=1/109, about0.917%. Total stored parameter entries are larger in the unmerged adapter object because the frozen base and the additional factors both remain present.

The output-head function is base_output(H)+(HAB)*(\(\frac{\alpha}{r}\)), with hidden states H shaped[B, T, 32]. In this fixture \(\alpha=r=2\), so the scale is one. B starts at zero and therefore preserves initial logits regardless of the random nonzero A. Comparing logits verifies function preservation, while exact parameter comparisons verify that the copied base states agree. The two checks answer different questions.

Only the final vocabulary mapping is adapted. Token embeddings, position embeddings, attention and feed-forward transformations remain fixed in that candidate. The full model can change all of them. This constrains which representation failures the adapter can repair. A low training loss from the output head may be sufficient for the tiny task, while a task requiring different hidden-state distinctions could need another target module or a different method.

The rank-two update has at most rank two, but its numerical rank can be smaller. For one hidden vector, many different factor pairs produce the same output adjustment. A parameter count does not identify a unique learned mechanism. Keep module placement, scale and actual singular-value or behavior checks separate from the configured rank label.

The full optimizer uses learning rate 0.01 and the adapter optimizer0.03, each for20 updates. These are fixed fixture settings rather than held-out selections, but they are not the same optimizer policy. A claim that one update method is inherently better cannot be isolated from those settings with this single run. A more informative study might allocate a declared tuning budget to each method using development data, then compare frozen choices on untouched families.

The frozen-state check snapshots every nontrainable adapted parameter and compares it exactly afterward. That can catch explicit accidental assignments even if requires_grad remains False. It does not prove the full absence of mutable nonparameter state in arbitrary architectures; models with BatchNorm or other buffers need those state objects checked too. This decoder uses LayerNorm and no running-batch-statistic buffers.

The held-out record again changes a prefix token while preserving a known second prompt token and answer. Both candidates are evaluated using teacher-forced active-target loss, without requiring a particular winner. A meaningful report should preserve those actual values, question identity and mask. It should not turn one finite loss comparison into evidence of natural-language generation, domain knowledge or source-grounded correctness.

### Interview reasoning with explanatory answers

**Why copy one state_dict instead of merely using one seed?** Model construction consumes random draws. Creating multiple models after one seed can yield different initial weights; copying the same state explicitly establishes the intended starting point.

**Does freezing the base guarantee no gradient is needed through it?** Not universally. If trainable modules precede a frozen block, derivatives may need to pass through that block to reach them. Here the only added trainable module is the output head, so the specific dependency structure is narrower.

**What does the 96-parameter result establish?** The trainable size of this output-head adapter. It does not measure peak memory, latency or the quality of adapting attention projections in a different architecture.

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

The question is: Evaluate prompt[7, 2] with answer[5, 3] for both candidates using the same mask.

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

**Expected:** adapter 96 entries; 20 updates each; scope literal-token task.

**Verify:** Compare the computed values or written argument with adapter 96 entries; 20 updates each; scope literal-token task.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

# llm-applied-015: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Full supervised fine-tuning updates all trainable model parameters on governed target examples. The operation can change representations, attention and output behavior together, which offers flexibility but also risks overfitting and forgetting. A working training loop is not evidence that a subject assistant has learned current facts or become reliable. The task data, mask, objective, optimizer and evaluation split define what the update actually means.

This chapter performs real CPU gradient updates on the course's small causal decoder. It has a literal vocabulary of 16 token IDs, width32, two attention heads and one block. The tokens stand for authored prompt and answer symbols, not natural-language competence. Two training sequences teach a simple answer pattern; a separately identified held-out prompt tests a small transfer case. We update every parameter for exactly20 steps and report training and held-out loss separately. No pretrained weights, external corpus or hosted model is used. The point is to make the mechanics, evidence and limitations of full SFT visible before using a larger stack.

**Full SFT:** Updating all trainable model parameters on supervised examples.

**Answer-only objective:** Loss over answer targets while prompt tokens remain context.

**Forgetting:** Loss of previously useful behavior after adaptation.

**Held-out transfer:** Behavior on records excluded from fitting and selection.

## Reading the implementation

Construct shifted inputs and answer-only labels, using-100 for the prompt-prediction position. Set a local seed before model creation. Adam receives all model parameters. Each step clears gradients, calculates logits, flattens the batch/time axes for cross entropy, backpropagates and applies one update. A detached clone records initial state. Evaluation usesmodel.eval andtorch.no_grad, then calculates the same active-target objective on held-out IDs.

## Trace the full-SFT state and objective

The model uses vocabulary16, width32, two attention heads and context capacity32. For a training batch with \(B=2\), \(T=3\), token and position embeddings combine into[2, 3, 32]. The QKV projection produces[2, 3, 96], then each component becomes[2, 2, 3, 16] after splitting into two heads. Attention scores have shape[2, 2, 3, 3], with a causal allowed-position relation. The output logits return to[2, 3, 16].

The trainable parameter ledger is explicit:

| Component | Entries |
| --- | --- |
| Token embedding16×32 | 512 |
| Position embedding32×32 | 1024 |
| Two LayerNorm scales and biases | 128 |
| Bias-free QKV32×96 | 3072 |
| Bias-free attention projection32×32 | 1024 |
| Feed-forward32→64→32 including biases | 4192 |
| Bias-free vocabulary projection32×16 | 512 |
| Total | 10464 |

No weights are tied in this decoder. Parameter count does not equal total training memory: gradients, Adam moment state, activations and temporary attention tensors contribute separately. The CPU example does not measure GPU peak allocation or optimizer sharding.

The two sequences yield four active targets:5, 3, 6, 3. For an independent zero-logit probe, each class initially has probability1/16 and each active event has loss log16. The mean over the four active events is still log16. At an active position, the target-logit gradient is(1/16-1)/4=-15/64, and every other class gradient is1/64. The ignored prompt-prediction positions have zero direct logit gradient. These derivatives explain both the mask and the denominator without relying on the trained decoder's internal state.

Each optimizer iteration computes loss at the current parameters, records it, backpropagates and then updates. Thus a20-entry curve records states before updates1 through20: its final element describes the model after19 updates. It is useful optimization history, but it is not the post-twentieth-update loss. The repaired final evaluation recomputes training and held-out objectives from the same frozen final state. This prevents a reporting label from mixing two parameter versions.

The objective is teacher-forced next-token cross entropy. It conditions each position on the supplied prefix, including previous true answer tokens. Autoregressive generation instead conditions later positions on its own earlier outputs. A lower teacher-forced loss does not guarantee exact generated answers or correct stopping behavior. The lesson deliberately evaluates token loss and parameter changes; it does not silently substitute them for a generation-quality test.

The held-out sequence[7, 2, 5, 3] changes the first prompt token while preserving the second prompt token 2 and the answer[5, 3]. A model could succeed by learning a shortcut from token 2 to5 and then to3, without using the first prompt token meaningfully. That makes the example a small transfer probe, not a demonstration of unseen factual reasoning. Multiple counterexamples that require both prompt components would be needed to assess compositional dependence.

The decoder returns a detached key/value cache, but this training objective discards it and uses full uncached sequences. Reusing that detached cache across training segments would change the gradient boundary. Treat it as an inference facility unless a separate truncated-training objective is explicitly designed and tested.

### Interview reasoning with explanatory answers

**What proves that full-model optimization occurred?** The optimizer receives all trainable parameters, updates actually run, losses are observed and an embedding parameter changes. This establishes a concrete update path, not that every scalar must change on every batch.

**Why recompute final loss?** The last logged training loss precedes the last optimizer step. A final-state comparison needs a fresh forward evaluation after all declared updates.

**Why can held-out token loss improve without domain competence?** The task may share a simple token shortcut, and teacher forcing differs from free generation. The fixture contains literal IDs and one visible transfer case, so broader claims require different evidence.

## Exercise 1: Build an explicit SFT batch

The question is: Use sequences[1, 2, 5, 3] and[1, 4, 6, 3], masking the first shifted target.

The first answer token is still supervised. The mask excludes predicting the prompt continuation, not the role of the prompt as conditioning context.

```python
torch.manual_seed(23); model=TinyDecoder(); sequences=torch.tensor([[1,2,5,3],[1,4,6,3]])
inputs=sequences[:,:-1]; labels=sequences[:,1:].clone(); labels[:,0]=-100
assert tuple(inputs.shape)==(2,3) and labels.tolist()==[[-100,5,3],[-100,6,3]] and int((labels!=-100).sum())==4
```

**Expected:** inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.

**Verify:** Compare the computed values or written argument with inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.

## Exercise 2: Measure the initial state

The question is: Calculate initial training loss and a held-out prompt loss before any update; count trainable parameters.

The held-out baseline is recorded before fitting, but it is not used to choose the update count. The fixed count defines the experiment in advance.

```python
held=torch.tensor([[7,2,5,3]]); held_labels=held[:,1:].clone(); held_labels[:,0]=-100
with torch.no_grad():
    initial_train=objective(model,inputs,labels).item(); initial_held=objective(model,held[:,:-1],held_labels).item()
count=sum(p.numel() for p in model.parameters() if p.requires_grad)
assert np.isfinite([initial_train,initial_held]).all() and 0<count<50000 and all(p.requires_grad for p in model.parameters())
```

**Expected:** both losses finite; all model parameters trainable; count below50000.

**Verify:** Compare the computed values or written argument with both losses finite; all model parameters trainable; count below50000.

## Exercise 3: Perform actual full fine-tuning

The question is: Run20 Adam updates atlearningrate.01, clearing gradients each time.

Checking an embedding parameter demonstrates that the update reaches more than the final output layer. A loss curve alone could be misleading if it came from a different object or cached tensor.

```python
before=model.token.weight.detach().clone(); opt=torch.optim.Adam(model.parameters(),lr=.01); curve=[]
for _ in range(20):
    opt.zero_grad(set_to_none=True); loss=objective(model,inputs,labels); curve.append(loss.item()); loss.backward(); opt.step()
assert len(curve)==20 and np.isfinite(curve).all() and curve[-1]<curve[0]
assert not torch.equal(before,model.token.weight.detach())
```

**Expected:** 20 finite losses; training loss decreases; an embedding parameter changes.

**Verify:** Compare the computed values or written argument with 20 finite losses; training loss decreases; an embedding parameter changes.

## Exercise 4: Inspect the mask derivative

The question is: Differentiate cross entropy with respect to fresh zero logits under the same labels.

The loss mask affects optimization, not merely the displayed average. This independent probe isolates target participation from the model architecture.

```python
probe=torch.zeros((2,3,16),requires_grad=True); F.cross_entropy(probe.reshape(-1,16),labels.reshape(-1),ignore_index=-100).backward()
assert torch.count_nonzero(probe.grad[:,0]).item()==0 and torch.count_nonzero(probe.grad[:,1:]).item()>0
```

**Expected:** ignored prompt positions have zero gradient; answer positions do not.

**Verify:** Compare the computed values or written argument with ignored prompt positions have zero gradient; answer positions do not.

## Exercise 5: Evaluate the frozen held-out prompt

The question is: After the declared20 updates, evaluate the held-out sequence without another optimizer step.

A held-out score may improve or worsen. The lesson reports the observation rather than requiring a favorable result that could encourage test-driven tuning.

```python
model.eval(); saved=model.output.weight.detach().clone()
with torch.no_grad():
    final_held=objective(model,held[:,:-1],held_labels).item()
    final_train=objective(model,inputs,labels).item()
assert np.isfinite(final_held) and torch.equal(saved,model.output.weight.detach())
```

**Expected:** finite held-out loss and unchanged weights during evaluation; no promised improvement.

**Verify:** Compare the computed values or written argument with finite held-out loss and unchanged weights during evaluation; no promised improvement.

## Exercise 6: Write an honest adaptation receipt

The question is: Record update count, active training targets, train/heldout losses and the literal-token limitation.

A real adaptation report should also include data/model hashes, environment and retained baseline tasks. The tiny receipt illustrates those evidence categories without overstating its task.

```python
receipt={'updates':20,'active_training_targets':4,'initial_train':initial_train,'final_train':final_train,'initial_held':initial_held,'final_held':final_held,'scope':'literal token task, not a pretrained subject assistant'}
assert receipt['updates']==20 and receipt['active_training_targets']==4 and 'not a pretrained' in receipt['scope']
with torch.no_grad(): np.testing.assert_allclose(receipt['final_train'],objective(model,inputs,labels).item(),atol=1e-12,rtol=0)
```

**Expected:** receipt says 20 updates, 4 active training targets and no natural-language competence claim.

**Verify:** Compare the computed values or written argument with receipt says 20 updates, 4 active training targets and no natural-language competence claim.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

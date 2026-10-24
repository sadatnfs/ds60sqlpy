# llm-applied-015: Full supervised fine-tuning of a tiny causal decoder

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-014`, `llm-028`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Full supervised fine-tuning makes the complete model available to the optimizer. This chapter follows one update from token inputs to parameter state, explains the role of Adam and teacher forcing, and shows how to read a tiny training result without turning it into a claim of domain expertise.

## Purpose and mental model

Full supervised fine-tuning updates all trainable model parameters on governed target examples. The operation can change representations, attention and output behavior together, which offers flexibility but also risks overfitting and forgetting. A working training loop is not evidence that a subject assistant has learned current facts or become reliable. The task data, mask, objective, optimizer and evaluation split define what the update actually means.

This chapter performs real CPU gradient updates on the course's small causal decoder. It has a literal vocabulary of 16 token IDs, width 32, two attention heads and one block. The tokens stand for authored prompt and answer symbols, not natural-language competence. Two training sequences teach a simple answer pattern; a separately identified held-out prompt tests a small transfer case. All model parameters are eligible for the 20 optimizer steps and report training and held-out loss separately. No pretrained weights, external corpus or hosted model is used. The point is to make the mechanics, evidence and limitations of full SFT visible before using a larger stack.

## Treat training as a state transition that can be inspected

The Methods Desk dataset now defines a behavior worth testing. Before using a pretrained model, the course reduces the machinery to a small causal decoder with literal token IDs. The reduction keeps the computation real: embeddings, attention, normalization, a feed-forward block, logits, loss, backward propagation and optimizer updates all execute. It removes the temptation to explain a successful run as natural-language understanding when the visible task can be examined directly.

Let theta_t denote the model state after t optimizer updates. A training iteration first evaluates the objective at theta_t, computes its gradient and then constructs theta_(t+1). The recorded loss belongs to the state at which it was evaluated. This is why the last value in a20-iteration pre-update curve describes theta_19, while a final post-training evaluation describes theta_20.

The qualified reference preserves that distinction. It recomputes final training loss from the frozen final state, alongside held-out loss. A report should identify which state produced each number. Otherwise a seemingly minor logging label can make two candidates or two datasets appear to have been evaluated at the same checkpoint when they were not.

## Follow the supervised signal through the decoder

The two training rows contain prompt and answer symbols. After shifting, the model receives three input positions per row and predicts a 16-way vocabulary distribution at each position. Only four target positions contribute to the answer objective. The shape ledger later in the chapter shows how a[2,3] token matrix becomes[2,3,32] hidden states, two attention heads and finally[2,3,16] logits.

At an active target position, cross entropy encourages the target logit relative to the other vocabulary logits. Its derivative contains the predicted class probabilities minus the target indicator, scaled by the active-event denominator. This local derivative then flows through the output projection, feed-forward and attention paths into earlier parameters. The independent zero-logit probe isolates that first step without relying on the randomly initialized decoder's output.

The ignored prompt-prediction positions have no direct loss term. Their representations can still influence later answer positions through causal attention, so prompt embeddings can receive gradients from the answer objective. That is the desired conditioning relationship. A mask that removed the prompt from the forward graph would define a different learning problem.

Full SFT describes the parameter set available for optimization. It does not require every scalar to change on every batch. An embedding row for a token never used as an input can have zero input-embedding gradient in this untied model. Unused position rows can likewise remain unchanged. The reference checks that all parameters are trainable and that an embedding tensor actually changes; it does not falsely require every entry to move.

## Adam adds optimizer state to model state

Ordinary gradient descent uses the current gradient directly. Adam also maintains moving estimates of its first and second moments. In a coordinatewise description, \(m_t=\beta_1m_{t-1}+(1-\beta_1)g_t\) and v_t=beta 2*v_(t-1)+(1-beta 2)*g_t². Bias-corrected versions divide by 1-beta \({1}^{t}\) and 1-beta \({2}^{t}\). The update then scales the first-moment estimate by the square root of the second-moment estimate plus epsilon. The versioned PyTorch documentation specifies the concrete implementation options. [PyTorch 2.9 Adam](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Adam.html).

Those moments are part of a training restart, even though they are not needed for ordinary model inference. Restoring only model weights and restarting Adam from empty state can produce a different trajectory. Learning-rate scheduling, random state and data order can add further restart requirements. The tiny exercise starts from a declared initial state and uses a fixed update count; it does not claim to implement a complete resumable training service.

Adaptive scaling also does not guarantee that every step lowers the objective or that the chosen learning rate is appropriate. The fixture requires finite logged values and an improvement over its initial loss. A realistic experiment should inspect unstable updates, parameter changes, gradients and validation behavior rather than treating the optimizer's name as a convergence certificate.

## Teacher-forced loss and generated answers are different observations

During training, each answer position sees the earlier correct answer tokens supplied by the dataset. During autoregressive generation, it sees its own earlier outputs. An early generation mistake can therefore change later inputs in a way that teacher-forced evaluation did not exercise. A lower token loss is useful evidence about the declared predictive objective, but it does not by itself establish exact-match generation or correct stopping.

The literal held-out row changes the first prompt token while retaining a familiar second prompt token and answer. A model could succeed by using the latter token as a shortcut and largely ignoring the changed prefix. That makes the row a small transfer probe, not a demonstration of reasoning about an unseen domain. More informative cases would vary the dependencies that the intended task requires and include changes that should and should not alter the answer.

A domain-assistant evaluation must also inspect the content of generated responses: unsupported fields, wrong units, invented citations, inappropriate refusals and regression on previously useful tasks. Those outcomes cannot be recovered from training loss alone. If the model learned an unsupported target from the dataset, successful optimization can make the error more consistent.

## Read a training receipt as evidence, not endorsement

A useful receipt identifies the data, model configuration, target mask, optimizer settings, update count and the state used for evaluation. It preserves both successes and failures. In this course, actual parameter changes and finite losses establish that the training machinery ran. The literal vocabulary, two training rows and one visible transfer row limit the task claim.

Forgetting and overfitting require separate observations. A candidate may improve the supervised task while worsening another capability, or may memorize the training templates without transferring. Keep baseline-retention tasks and untouched evaluation families when the experiment moves to a realistic domain dataset. The next chapter constrains the update through low-rank factors, but the need for those measurements remains.

## Design decisions and when to use this method

Use full SFT when a measured task requires enough flexibility to justify updating the complete model and the compute, governance and regression-testing costs are acceptable. Compare it with prompt and adapter baselines under the same data and evaluation contract. A larger trainable parameter count can fit a small dataset quickly while worsening transfer, so keep validation and baseline-retention checks separate.

Do not interpret a lower training loss as proof of domain expertise. It can reflect memorization, target leakage or a task-specific shortcut. For a realistic pretrained model, preserve chat-template compatibility, label masks, sequence truncation policy and tokenizer revision. Measure output support and task utility, not only token loss. Keep a rollback artifact and evaluate unrelated baseline capabilities to detect forgetting before considering deployment.

Use the tiny decoder to inspect a complete gradient-update path before scaling the training stack. Record the actual model, target mask and state being measured. The review repairs the final training receipt to recompute loss after the twentieth update, matching the state used for final held-out evaluation.

Keep retention tasks and multiple independent answer families when evaluating real adaptation. This fixture has two training sequences and one visible held-out prefix. Its purpose is bounded optimization evidence, not a claim of natural-language or domain competence.

## Vocabulary and concepts

**Full SFT:** Updating all trainable model parameters on supervised examples.

**Answer-only objective:** Loss over answer targets while prompt tokens remain context.

**Forgetting:** Loss of previously useful behavior after adaptation.

**Held-out transfer:** Behavior on records excluded from fitting and selection.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-015/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `llm-torch-cpu` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-015.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Construct shifted inputs and answer-only labels, using-100 for the prompt-prediction position. Set a local seed before model creation. Adam receives all model parameters. Each step clears gradients, calculates logits, flattens the batch/time axes for cross entropy, backpropagates and applies one update. A detached clone records initial state. Evaluation uses model.eval and torch.no_grad, then calculates the same active-target objective on held-out IDs.

## Trace the full-SFT state and objective

The model uses vocabulary 16, width 32, two attention heads and context capacity 32. For a training batch with \(B=2\), \(T=3\), token and position embeddings combine into[2, 3, 32]. The QKV projection produces[2, 3, 96], then each component becomes[2, 2, 3, 16] after splitting into two heads. Attention scores have shape[2, 2, 3, 3], with a causal allowed-position relation. The output logits return to[2, 3, 16].

The trainable parameter ledger is explicit:

| Component | Entries |
| --- | --- |
| Token embedding 16×32 | 512 |
| Position embedding 32×32 | 1024 |
| Two LayerNorm scales and biases | 128 |
| Bias-free QKV 32×96 | 3072 |
| Bias-free attention projection 32×32 | 1024 |
| Feed-forward 32→64→32 including biases | 4192 |
| Bias-free vocabulary projection 32×16 | 512 |
| Total | 10464 |

No weights are tied in this decoder. Parameter count does not equal total training memory: gradients, Adam moment state, activations and temporary attention tensors contribute separately. The CPU example does not measure GPU peak allocation or optimizer sharding.

The two sequences yield four active targets:5, 3, 6, 3. For an independent zero-logit probe, each class initially has probability \(\frac{1}{16}\) and each active event has loss log16. The mean over the four active events is still log16. At an active position, the target-logit gradient is(\(\frac{1}{16}\)-1)/4=-15/64, and every other class gradient is \(\frac{1}{64}\). The ignored prompt-prediction positions have zero direct logit gradient. These derivatives explain both the mask and the denominator without relying on the trained decoder's internal state.

Each optimizer iteration computes loss at the current parameters, records it, backpropagates and then updates. Thus a 20-entry curve records states before updates 1 through 20: its final element describes the model after 19 updates. It is useful optimization history, but it is not the post-twentieth-update loss. The repaired final evaluation recomputes training and held-out objectives from the same frozen final state. This prevents a reporting label from mixing two parameter versions.

The objective is teacher-forced next-token cross entropy. It conditions each position on the supplied prefix, including previous true answer tokens. Autoregressive generation instead conditions later positions on its own earlier outputs. A lower teacher-forced loss does not guarantee exact generated answers or correct stopping behavior. The lesson deliberately evaluates token loss and parameter changes; it does not silently substitute them for a generation-quality test.

The held-out sequence[7, 2, 5, 3] changes the first prompt token while preserving the second prompt token 2 and the answer[5, 3]. A model could succeed by learning a shortcut from token 2 to 5 and then to 3, without using the first prompt token meaningfully. That makes the example a small transfer probe, not a demonstration of unseen factual reasoning. Multiple counterexamples that require both prompt components would be needed to assess compositional dependence.

The decoder returns a detached key/value cache, but this training objective discards it and uses full uncached sequences. Reusing that detached cache across training segments would change the gradient boundary. Treat it as an inference facility unless a separate truncated-training objective is explicitly designed and tested.

### Interview reasoning with explanatory answers

**What proves that full-model optimization occurred?** The optimizer receives all trainable parameters, updates actually run, losses are observed and an embedding parameter changes. This establishes a concrete update path, not that every scalar must change on every batch.

**Why recompute final loss?** The last logged training loss precedes the last optimizer step. A final-state comparison needs a fresh forward evaluation after all declared updates.

**Why can held-out token loss improve without domain competence?** The task may share a simple token shortcut, and teacher forcing differs from free generation. The fixture contains literal IDs and one visible transfer case, so broader claims require different evidence.

## Worked example / walkthrough

### Example A: Build an explicit SFT batch

The first answer token is still supervised. The mask excludes predicting the prompt continuation, not the role of the prompt as conditioning context.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
class TinyDecoder(nn.Module):
    def __init__(self,vocab=16,width=32,heads=2,context=32):
        super().__init__()
        self.vocab,self.width,self.heads,self.context=vocab,width,heads,context
        self.token=nn.Embedding(vocab,width); self.position=nn.Embedding(context,width)
        self.norm1=nn.LayerNorm(width); self.qkv=nn.Linear(width,3*width,bias=False)
        self.projection=nn.Linear(width,width,bias=False); self.norm2=nn.LayerNorm(width)
        self.feed=nn.Sequential(nn.Linear(width,2*width),nn.ReLU(),nn.Linear(2*width,width))
        self.output=nn.Linear(width,vocab,bias=False)
    def forward(self,ids,cache=None):
        if ids.ndim!=2 or ids.dtype!=torch.long or ids.shape[1]==0: raise ValueError('nonempty long batch,time IDs')
        offset=0 if cache is None else cache['k'].shape[2]
        batch,time=ids.shape
        if offset+time>self.context or torch.any(ids<0) or torch.any(ids>=self.vocab): raise ValueError('context or vocabulary limit')
        x=self.token(ids)+self.position(torch.arange(offset,offset+time))
        q,k,v=self.qkv(self.norm1(x)).chunk(3,dim=-1)
        def split(t): return t.reshape(batch,time,self.heads,self.width//self.heads).transpose(1,2)
        q,k,v=map(split,(q,k,v))
        if cache is not None:
            if cache['k'].shape[0]!=batch: raise ValueError('cache batch mismatch')
            k=torch.cat([cache['k'],k],dim=2); v=torch.cat([cache['v'],v],dim=2)
        allowed=torch.arange(k.shape[2])[None,:]<=torch.arange(offset,offset+time)[:,None]
        scores=q@k.transpose(-2,-1)/(self.width//self.heads)**.5
        weights=torch.softmax(scores.masked_fill(~allowed,float('-inf')),dim=-1)
        mixed=(weights@v).transpose(1,2).contiguous().reshape(batch,time,self.width)
        x=x+self.projection(mixed); x=x+self.feed(self.norm2(x))
        return self.output(x),{'k':k.detach(),'v':v.detach()}

def objective(model,inputs,labels):
    logits,_=model(inputs)
    return F.cross_entropy(logits.reshape(-1,model.vocab),labels.reshape(-1),ignore_index=-100)
torch.manual_seed(23); model=TinyDecoder(); sequences=torch.tensor([[1,2,5,3],[1,4,6,3]])
inputs=sequences[:,:-1]; labels=sequences[:,1:].clone(); labels[:,0]=-100
assert tuple(inputs.shape)==(2,3) and labels.tolist()==[[-100,5,3],[-100,6,3]] and int((labels!=-100).sum())==4
```

**Expected:** inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.

### Example B: Measure the initial state

The held-out baseline is recorded before fitting, but it is not used to choose the update count. The fixed count defines the experiment in advance.

```python
held=torch.tensor([[7,2,5,3]]); held_labels=held[:,1:].clone(); held_labels[:,0]=-100
with torch.no_grad():
    initial_train=objective(model,inputs,labels).item(); initial_held=objective(model,held[:,:-1],held_labels).item()
count=sum(p.numel() for p in model.parameters() if p.requires_grad)
assert np.isfinite([initial_train,initial_held]).all() and 0<count<50000 and all(p.requires_grad for p in model.parameters())
```

**Expected:** both losses finite; all model parameters trainable; count below 50000.

### Example C: Perform actual full fine-tuning

Checking an embedding parameter demonstrates that the update reaches more than the final output layer. A loss curve alone could be misleading if it came from a different object or cached tensor.

```python
before=model.token.weight.detach().clone(); opt=torch.optim.Adam(model.parameters(),lr=.01); curve=[]
for _ in range(20):
    opt.zero_grad(set_to_none=True); loss=objective(model,inputs,labels); curve.append(loss.item()); loss.backward(); opt.step()
assert len(curve)==20 and np.isfinite(curve).all() and curve[-1]<curve[0]
assert not torch.equal(before,model.token.weight.detach())
```

**Expected:** 20 finite losses; training loss decreases; an embedding parameter changes.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets. receipt says 20 updates, 4 active training targets and no natural-language competence claim. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Build an explicit SFT batch.** Use sequences[1, 2, 5, 3] and[1, 4, 6, 3], masking the first shifted target.
   **Expected:** inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.
   **Verify:** Save the assertion results for exercise 1, including inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.

2. **Measure the initial state.** Calculate initial training loss and a held-out prompt loss before any update; count trainable parameters.
   **Expected:** both losses finite; all model parameters trainable; count below 50000.
   **Verify:** Save the assertion results for exercise 2, including both losses finite; all model parameters trainable; count below 50000.

3. **Perform actual full fine-tuning.** Run 20 Adam updates at learning rate 0.01, clearing gradients each time.
   **Expected:** 20 finite losses; training loss decreases; an embedding parameter changes.
   **Verify:** Save the assertion results for exercise 3, including 20 finite losses; training loss decreases; an embedding parameter changes.

4. **Inspect the mask derivative.** Differentiate cross entropy with respect to fresh zero logits under the same labels.
   **Expected:** ignored prompt positions have zero gradient; answer positions do not.
   **Verify:** Save the assertion results for exercise 4, including ignored prompt positions have zero gradient; answer positions do not.

5. **Evaluate the frozen held-out prompt.** After the declared 20 updates, evaluate the held-out sequence without another optimizer step.
   **Expected:** finite held-out loss and unchanged weights during evaluation; no promised improvement.
   **Verify:** Save the assertion results for exercise 5, including finite held-out loss and unchanged weights during evaluation; no promised improvement.

6. **Write an honest adaptation receipt.** Record update count, active training targets, train/heldout losses and the literal-token limitation.
   **Expected:** receipt says 20 updates, 4 active training targets and no natural-language competence claim.
   **Verify:** Save the assertion results for exercise 6, including receipt says 20 updates, 4 active training targets and no natural-language competence claim.

## Common pitfalls and diagnosis

If a curve decreases but parameters do not change, verify that the optimizer owns the model being evaluated and that step executes. If a reported final loss disagrees with a saved model, inspect whether it was measured before or after the final update. If mask gradients appear diluted, count active target positions rather than all stored logits.

If held-out success disappears after changing the second prompt token, investigate the shortcut encoded by the tiny task. If generation fails despite better teacher-forced loss, inspect rollout, decoding and stop-token behavior separately. If a cache is reused during training, document its detached gradient boundary before interpreting the update as full-sequence learning.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Full SFT, Answer-only objective, Forgetting using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-014`, `llm-028` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch training mechanics](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-015, Full supervised fine-tuning of a tiny causal decoder.
Read courses/llm-applied/guides/llm-applied-015.md and courses/llm-applied/lessons/llm-applied-015.py. Direct prerequisites: `llm-applied-014`, `llm-028`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

# llm-applied-015: Full supervised fine-tuning of a tiny causal decoder

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-014`, `llm-028`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Full supervised fine-tuning updates all trainable model parameters on governed target examples. The central investigation is concrete: Use sequences[1, 2, 5, 3] and[1, 4, 6, 3], masking the first shifted target. The finish condition is inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets. receipt says20 updates, 4 active training targets and no natural-language competence claim. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Full supervised fine-tuning updates all trainable model parameters on governed target examples. The operation can change representations, attention and output behavior together, which offers flexibility but also risks overfitting and forgetting. A working training loop is not evidence that a subject assistant has learned current facts or become reliable. The task data, mask, objective, optimizer and evaluation split define what the update actually means.

This chapter performs real CPU gradient updates on the course's small causal decoder. It has a literal vocabulary of 16 token IDs, width32, two attention heads and one block. The tokens stand for authored prompt and answer symbols, not natural-language competence. Two training sequences teach a simple answer pattern; a separately identified held-out prompt tests a small transfer case. We update every parameter for exactly20 steps and report training and held-out loss separately. No pretrained weights, external corpus or hosted model is used. The point is to make the mechanics, evidence and limitations of full SFT visible before using a larger stack.

## Design decisions and when to use this method

Use full SFT when a measured task requires enough flexibility to justify updating the complete model and the compute, governance and regression-testing costs are acceptable. Compare it with prompt and adapter baselines under the same data and evaluation contract. A larger trainable parameter count can fit a small dataset quickly while worsening transfer, so keep validation and baseline-retention checks separate.

Do not interpret a lower training loss as proof of domain expertise. It can reflect memorization, target leakage or a task-specific shortcut. For a realistic pretrained model, preserve chat-template compatibility, label masks, sequence truncation policy and tokenizer revision. Measure output support and task utility, not only token loss. Keep a rollback artifact and evaluate unrelated baseline capabilities to detect forgetting before considering deployment.

## Vocabulary and concepts

**Full SFT:** Updating all trainable model parameters on supervised examples.

**Answer-only objective:** Loss over answer targets while prompt tokens remain context.

**Forgetting:** Loss of previously useful behavior after adaptation.

**Held-out transfer:** Behavior on records excluded from fitting and selection.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-015/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-015.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-015.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Construct shifted inputs and answer-only labels, using-100 for the prompt-prediction position. Set a local seed before model creation. Adam receives all model parameters. Each step clears gradients, calculates logits, flattens the batch/time axes for cross entropy, backpropagates and applies one update. A detached clone records initial state. Evaluation usesmodel.eval andtorch.no_grad, then calculates the same active-target objective on held-out IDs.

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

**Expected:** both losses finite; all model parameters trainable; count below50000.

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

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets. receipt says20 updates, 4 active training targets and no natural-language competence claim. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Build an explicit SFT batch.** Use sequences[1, 2, 5, 3] and[1, 4, 6, 3], masking the first shifted target.
   **Expected:** inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.
   **Verify:** Save the assertion results for exercise 1, including inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.

2. **Measure the initial state.** Calculate initial training loss and a held-out prompt loss before any update; count trainable parameters.
   **Expected:** both losses finite; all model parameters trainable; count below50000.
   **Verify:** Save the assertion results for exercise 2, including both losses finite; all model parameters trainable; count below50000.

3. **Perform actual full fine-tuning.** Run20 Adam updates atlearningrate.01, clearing gradients each time.
   **Expected:** 20 finite losses; training loss decreases; an embedding parameter changes.
   **Verify:** Save the assertion results for exercise 3, including 20 finite losses; training loss decreases; an embedding parameter changes.

4. **Inspect the mask derivative.** Differentiate cross entropy with respect to fresh zero logits under the samelabels.
   **Expected:** ignored prompt positions have zero gradient; answer positions do not.
   **Verify:** Save the assertion results for exercise 4, including ignored prompt positions have zero gradient; answer positions do not.

5. **Evaluate the frozen held-out prompt.** After the declared20 updates, evaluate the held-out sequence without another optimizer step.
   **Expected:** finite held-out loss and unchanged weights during evaluation; no promised improvement.
   **Verify:** Save the assertion results for exercise 5, including finite held-out loss and unchanged weights during evaluation; no promised improvement.

6. **Write an honest adaptation receipt.** Record update count, active training targets, train/heldout losses and the literal-token limitation.
   **Expected:** receipt says20 updates, 4 active training targets and no natural-language competence claim.
   **Verify:** Save the assertion results for exercise 6, including receipt says20 updates, 4 active training targets and no natural-language competence claim.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Full SFT, Answer-only objective, Forgetting using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-014`, `llm-028` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch training mechanics](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-015, Full supervised fine-tuning of a tiny causal decoder.
Read courses/llm-applied/guides/llm-applied-015.md and courses/llm-applied/lessons/llm-applied-015.py. Direct prerequisites: `llm-applied-014`, `llm-028`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

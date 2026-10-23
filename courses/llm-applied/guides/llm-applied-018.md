# llm-applied-018: Compare full and adapter fine-tuning on frozen tasks

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-017`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A fair adaptation comparison starts both candidates from the same base state and uses the same training examples, target masks and held-out tasks. The central investigation is concrete: Create a seed 31 decoder and copy its state into full and adapted candidates. The finish condition is all initial base parameters equal. adapter96 entries; 20 updates each; scope literal-token task. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A fair adaptation comparison starts both candidates from the same base state and uses the same training examples, target masks and held-out tasks. Full SFT can change every parameter; an output-head LoRA adapter changes only a constrained set. Different trainable counts are expected, but they do not by themselves establish quality, speed or memory superiority. Keep optimization budgets and learning-rate policies explicit, and avoid selecting a winner from training loss alone.

This chapter trains two real tiny decoders on the same literal answer task. One updates the whole model; the other freezes the base and adds rank 2 adaptation to its vocabulary output projection. That placement is intentionally narrow and is not claimed to match a production LoRA configuration across attention and feed-forward modules. Both run20 updates. We compare held-out losses without requiring a particular winner, verify frozen-base bytes and prove that an unmodified adapter initially preserves base predictions. A useful result includes limitations and failure cases, not only a ranking.

## Design decisions and when to use this method

Use an adaptation comparison when the team is deciding whether a behavior gap justifies weight updates and which update strategy fits the constraints. Keep a prompt-only and retrieval baseline available as well. Evaluate held-out task families, unsupported answers, formatting and baseline retention rather than selecting only by token loss.

Do not generalize this output-head-only experiment to every LoRA configuration. Adapters in attention or feed-forward projections can change different representations. Rank, scaling, target modules, dropout and optimizer policy all affect the result. A realistic study should report actual wall time and peak memory on the prepared hardware, with warmup and batching policies fixed. The tiny experiment supplies the state and evaluation checks needed to make that larger comparison interpretable.

## Vocabulary and concepts

**Controlled adaptation comparison:** Candidates sharing base state,data and evaluation contract.

**Target module:** The specific layer receiving an adapter update.

**Frozen-state proof:** Exact comparison of parameters required to remain unchanged.

**Task transfer metric:** Held-out behavior measured after adaptation under a fixed rubric.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-018/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-018.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-018.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Create one base model, copy itsstate_dict into two new instances, and snapshot the initial logits. Freeze every parameter in the adapter candidate before replacing its output projection withLoRAHead. Optimize onlyparameters withrequires_gradTrue. Keep the full and adapter optimizers separate. Evaluate both with the same held-out labels underno_grad. The output head has input width32 and vocabulary16, so rank 2 adds96 trainable entries.

## Worked example / walkthrough

### Example A: Clone one base into two candidates

Independent model objects prevent one optimizer from changing the other candidate. Equal initial state is stronger than merely reusing the same architecture name.

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
class LoRAHead(nn.Module):
    def __init__(self,base,rank=2,alpha=2):
        super().__init__(); self.base=base; self.rank=rank; self.scale=alpha/rank
        for parameter in base.parameters(): parameter.requires_grad_(False)
        self.a=nn.Parameter(torch.randn(base.in_features,rank)*.02)
        self.b=nn.Parameter(torch.zeros(rank,base.out_features))
    def forward(self,x): return self.base(x)+(x@self.a@self.b)*self.scale

def objective(model,inputs,labels):
    logits,_=model(inputs)
    return F.cross_entropy(logits.reshape(-1,model.vocab),labels.reshape(-1),ignore_index=-100)
torch.manual_seed(31); base=TinyDecoder(); full=TinyDecoder(); adapted=TinyDecoder(); full.load_state_dict(base.state_dict()); adapted.load_state_dict(base.state_dict())
assert all(torch.equal(a,b) for a,b in zip(full.parameters(),adapted.parameters()))
```

**Expected:** all initial base parameters equal.

### Example B: Install an output-head adapter

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

### Example C: Train both candidates under fixed budgets

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

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: all initial base parameters equal. adapter96 entries; 20 updates each; scope literal-token task. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Clone one base into two candidates.** Create a seed 31 decoder and copy its state into full and adapted candidates.
   **Expected:** all initial base parameters equal.
   **Verify:** Save the assertion results for exercise 1, including all initial base parameters equal.

2. **Install an output-head adapter.** Freeze the adapted model, replace its output layer withrank2LoRA, and compare initial logits.
   **Expected:** 96 trainable adapter entries; initial logits match base.
   **Verify:** Save the assertion results for exercise 2, including 96 trainable adapter entries; initial logits match base.

3. **Train both candidates under fixed budgets.** Run20 full-SFT updates at.01 and20 adapter updates at.03 on the same masked batch.
   **Expected:** both training losses decrease; all logged values finite.
   **Verify:** Save the assertion results for exercise 3, including both training losses decrease; all logged values finite.

4. **Prove base preservation.** Compare every frozen adapted-model parameter against its saved copy.
   **Expected:** all frozen tensors exactly equal.
   **Verify:** Save the assertion results for exercise 4, including all frozen tensors exactly equal.

5. **Compare a frozen held-out task.** Evaluate prompt[7, 2] withanswer[5, 3] for both candidates using the same mask.
   **Expected:** two finite held-out losses; no predetermined winner.
   **Verify:** Save the assertion results for exercise 5, including two finite held-out losses; no predetermined winner.

6. **Record comparison limits.** Build a report with trainable counts, update budgets, target module and task scope.
   **Expected:** adapter96 entries; 20 updates each; scope literal-token task.
   **Verify:** Save the assertion results for exercise 6, including adapter96 entries; 20 updates each; scope literal-token task.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Controlled adaptation comparison, Target module, Frozen-state proof using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-017` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [LoRA](https://arxiv.org/abs/2106.09685), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-018, Compare full and adapter fine-tuning on frozen tasks.
Read courses/llm-applied/guides/llm-applied-018.md and courses/llm-applied/lessons/llm-applied-018.py. Direct prerequisites: `llm-applied-017`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

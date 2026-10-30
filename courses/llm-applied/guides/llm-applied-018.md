# llm-applied-018: Compare full and adapter fine-tuning on frozen tasks

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-017`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

An adaptation comparison is an experiment over complete configurations. This chapter explains how to align starting states, data, objectives and budgets, then connects parameter-level checks to a defensible choice for a subject-matter assistant.

## Purpose and mental model

A fair adaptation comparison starts both candidates from the same base state and uses the same training examples, target masks and held-out tasks. Full SFT can change every parameter; an output-head LoRA adapter changes only a constrained set. Different trainable counts are expected, but they do not by themselves establish quality, speed or memory superiority. Keep optimization budgets and learning-rate policies explicit, and avoid selecting a winner from training loss alone.

This chapter trains two real tiny decoders on the same literal answer task. One updates the whole model; the other freezes the base and adds rank 2 adaptation to its vocabulary output projection. That placement is intentionally narrow and is not claimed to match a production LoRA configuration across attention and feed-forward modules. Both run 20 updates. We compare held-out losses without requiring a particular winner, verify frozen-base bytes and prove that an unmodified adapter initially preserves base predictions. A useful result includes limitations and failure cases, not only a ranking.

## State the decision the comparison is meant to support

The Methods Desk team is deciding whether a stable response-format gap justifies adaptation and, if so, which update strategy is useful. Full SFT and LoRA are candidate mechanisms, but the actual decision also depends on the dataset, target modules, optimizer policy, serving constraints and quality rubric. A comparison should name that decision before collecting a favorable score.

One question is whether a small output-head adapter can fit the literal token task. Another is whether a realistic adapter improves supported domain answers under a memory budget. A third is whether full SFT retains useful general behavior after specializing. These questions require different evidence. The runnable experiment answers a narrow version of the first while establishing state controls that transfer to larger studies.

The unadapted prompt and retrieval baselines remain relevant. If the task is already solved by supplying the correct current definition and validating the output, training may add cost without addressing a necessary gap. If adaptation helps formatting but factual support remains limited by missing evidence, the final architecture may still need retrieval and tools.

## Align what should be held fixed

Copying one base state into independent model objects establishes a common starting function. Merely constructing two models after setting one global seed can produce different initial values because construction consumes random draws. The explicit state copy in the fixture is therefore a meaningful experimental control.

The candidates also share training examples, shifted inputs, answer masks and held-out records. Those controls keep the supervised events comparable. Separate optimizer objects prevent one candidate's state from influencing the other. Frozen-base snapshots verify that the adapter candidate preserves the values that its design says should remain fixed.

Some conditions necessarily differ. The full candidate has 10464 trainable parameters, while the output-head adapter has 96. Their hypothesis spaces are different by design. The fixed learning rates also differ in the fixture. A result can compare those complete configurations, but it cannot isolate an abstract method effect from every associated choice.

## Equal steps are one budget, not every budget

Twenty optimizer updates for each candidate align update count. They do not guarantee equal wall time, memory, gradient computation or optimization difficulty. An adapter can reduce trainable state while still running the base forward computation. Longer sequences can shift the dominant cost toward activations and attention rather than parameter updates.

A practical study can choose a resource constraint that matches the decision: equal data exposure, equal update count, equal tuning budget or a fixed time/memory limit. It should report the resulting tradeoff rather than imply that one comparison is universally fair. If each method receives hyperparameter tuning, keep that selection on development data and record the budget used to choose its final configuration.

Serving adds another dimension. An unmerged adapter can support switching among task variants while retaining a shared base. A merged artifact can change inference structure and deployment handling. Those choices affect operational complexity and must be tested under the intended dtype, model mode and artifact identity. Training parameter count alone does not settle them.

## Evaluate the behavior that motivated adaptation

Teacher-forced token loss measures the probability assigned to target continuations under supplied prefixes. It is useful for optimization diagnosis, but the Methods Desk needs more: valid structured fields, source-supported claims, correct calculations, appropriate unknowns and retention of relevant baseline behavior. A model can improve one of those dimensions while worsening another.

The tiny held-out row changes a prefix token but preserves a familiar answer pattern. It is deliberately not required to favor either candidate. That is an important testing principle: a held-out result is an observation to report, not an assertion that must be made favorable by tuning against it. The fixed fixture can reveal a mechanics failure without pretending to establish broad generalization.

A larger study should preserve actual generated outputs and their evidence context. If an adapted model uses the right field names but invents a denominator, format accuracy and grounded correctness must remain separate. If it refuses more requests, coverage belongs beside conditional quality. If it improves the target task but loses another useful capability, that regression is part of the decision rather than an unrelated inconvenience.

## Interpret a difference at the correct level

A lower loss for one candidate can arise from capacity, optimization policy, data fit or a useful inductive restriction. One run cannot identify all of those mechanisms. Paired evaluation over the same questions and repeated training where relevant can make the conclusion more informative, but the analysis must still match the observed design.

The output-head-only adapter also limits the scope of a negative result. Failure at that placement does not show that every LoRA configuration would fail, because adapters in attention or feed-forward modules can change different computations. Conversely, success on the tiny head task does not establish that the same rank and placement suit a pretrained domain assistant.

The report should retain the base identity, trainable set, target modules, rank/scale, optimizer settings, data and mask identities, update budget, evaluation artifacts and failure cases. This is the bridge from a reproducible training exercise to an engineering decision. The following preference and retrieval-training chapters change the objective again, so they need the same discipline about what signal is being optimized and what useful behavior is actually measured.

## Design decisions and when to use this method

Use an adaptation comparison when the team is deciding whether a behavior gap justifies weight updates and which update strategy fits the constraints. Keep a prompt-only and retrieval baseline available as well. Evaluate held-out task families, unsupported answers, formatting and baseline retention rather than selecting only by token loss.

Do not generalize this output-head-only experiment to every LoRA configuration. Adapters in attention or feed-forward projections can change different representations. Rank, scaling, target modules, dropout and optimizer policy all affect the result. A realistic study should report actual wall time and peak memory on the prepared hardware, with warmup and batching policies fixed. The tiny experiment supplies the state and evaluation checks needed to make that larger comparison interpretable.

Use the shared-base comparison to answer a specific engineering question: can a constrained output-head update address the declared token task under the chosen budget? Do not interpret that as a universal comparison of all LoRA placements or all pretrained adaptation methods.

Keep independent model objects and optimizers, shared initial state, the same supervised events and a fixed evaluation protocol. Report learning rates and parameter ownership alongside step counts. Equal numbers of steps do not make the amount of computation or the optimization problem identical.

## Vocabulary and concepts

**Controlled adaptation comparison:** Candidates sharing base state,data and evaluation contract.

**Target module:** The specific layer receiving an adapter update.

**Frozen-state proof:** Exact comparison of parameters required to remain unchanged.

**Task transfer metric:** Held-out behavior measured after adaptation under a fixed rubric.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-018/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `llm-torch-cpu` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-018.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Create one base model, copy its state_dict into two new instances, and snapshot the initial logits. Freeze every parameter in the adapter candidate before replacing its output projection with LoRAHead. Optimize only parameters with requires_grad=True. Keep the full and adapter optimizers separate. Evaluate both with the same held-out labels under no_grad. The output head has input width 32 and vocabulary 16, so rank 2 adds 96 trainable entries.

## Trace the two candidate models from one base

The full candidate starts with 10464 trainable parameters from the decoder ledger. The adapter candidate retains those base values frozen and adds A[32, 2] and B[2, 16] to the output projection, for \(64+32=96\) trainable entries. The trainable ratio is \(\frac{96}{10464}=\frac{1}{109}\), about 0.917%. Total stored parameter entries are larger in the unmerged adapter object because the frozen base and the additional factors both remain present.

The output-head function is base_output(H)+(HAB)*(\(\frac{\alpha}{r}\)), with hidden states H shaped[B, T, 32]. In this fixture \(\alpha=r=2\), so the scale is one. B starts at zero and therefore preserves initial logits regardless of the random nonzero A. Comparing logits verifies function preservation, while exact parameter comparisons verify that the copied base states agree. The two checks answer different questions.

Only the final vocabulary mapping is adapted. Token embeddings, position embeddings, attention and feed-forward transformations remain fixed in that candidate. The full model can change all of them. This constrains which representation failures the adapter can repair. A low training loss from the output head may be sufficient for the tiny task, while a task requiring different hidden-state distinctions could need another target module or a different method.

The rank-two update has at most rank two, but its numerical rank can be smaller. For one hidden vector, many different factor pairs produce the same output adjustment. A parameter count does not identify a unique learned mechanism. Keep module placement, scale and actual singular-value or behavior checks separate from the configured rank label.

The full optimizer uses learning rate 0.01 and the adapter optimizer 0.03, each for 20 updates. These are fixed fixture settings rather than held-out selections, but they are not the same optimizer policy. A claim that one update method is inherently better cannot be isolated from those settings with this single run. A more informative study might allocate a declared tuning budget to each method using development data, then compare frozen choices on untouched families.

The frozen-state check snapshots every nontrainable adapted parameter and compares it exactly afterward. That can catch explicit accidental assignments even if requires_grad remains False. It does not prove the full absence of mutable nonparameter state in arbitrary architectures; models with BatchNorm or other buffers need those state objects checked too. This decoder uses LayerNorm and no running-batch-statistic buffers.

The held-out record again changes a prefix token while preserving a known second prompt token and answer. Both candidates are evaluated using teacher-forced active-target loss, without requiring a particular winner. A meaningful report should preserve those actual values, question identity and mask. It should not turn one finite loss comparison into evidence of natural-language generation, domain knowledge or source-grounded correctness.

### Interview reasoning with explanatory answers

**Why copy one state_dict instead of merely using one seed?** Model construction consumes random draws. Creating multiple models after one seed can yield different initial weights; copying the same state explicitly establishes the intended starting point.

**Does freezing the base guarantee no gradient is needed through it?** Not universally. If trainable modules precede a frozen block, derivatives may need to pass through that block to reach them. Here the only added trainable module is the output head, so the specific dependency structure is narrower.

**What does the 96-parameter result establish?** The trainable size of this output-head adapter. It does not measure peak memory, latency or the quality of adapting attention projections in a different architecture.

## Worked example / walkthrough

### Example A: Clone one base into two candidates

Independent model objects prevent one optimizer from changing the other candidate. Equal initial state is stronger than merely reusing the same architecture name.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


class TinyDecoder(nn.Module):
    def __init__(self, vocab=16, width=32, heads=2, context=32):
        super().__init__()
        self.vocab, self.width, self.heads, self.context = vocab, width, heads, context
        self.token = nn.Embedding(vocab, width)
        self.position = nn.Embedding(context, width)
        self.norm1 = nn.LayerNorm(width)
        self.qkv = nn.Linear(width, 3 * width, bias=False)
        self.projection = nn.Linear(width, width, bias=False)
        self.norm2 = nn.LayerNorm(width)
        self.feed = nn.Sequential(
            nn.Linear(width, 2 * width), nn.ReLU(), nn.Linear(2 * width, width)
        )
        self.output = nn.Linear(width, vocab, bias=False)

    def forward(self, ids, cache=None):
        if ids.ndim != 2 or ids.dtype != torch.long or ids.shape[1] == 0:
            raise ValueError("nonempty long batch,time IDs")
        offset = 0 if cache is None else cache["k"].shape[2]
        batch, time = ids.shape
        if offset + time > self.context or torch.any(ids < 0) or torch.any(ids >= self.vocab):
            raise ValueError("context or vocabulary limit")
        x = self.token(ids) + self.position(torch.arange(offset, offset + time))
        q, k, v = self.qkv(self.norm1(x)).chunk(3, dim=-1)

        def split(t):
            return t.reshape(batch, time, self.heads, self.width // self.heads).transpose(1, 2)

        q, k, v = map(split, (q, k, v))
        if cache is not None:
            if cache["k"].shape[0] != batch:
                raise ValueError("cache batch mismatch")
            k = torch.cat([cache["k"], k], dim=2)
            v = torch.cat([cache["v"], v], dim=2)
        allowed = torch.arange(k.shape[2])[None, :] <= torch.arange(offset, offset + time)[:, None]
        scores = q @ k.transpose(-2, -1) / (self.width // self.heads) ** 0.5
        weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        mixed = (weights @ v).transpose(1, 2).contiguous().reshape(batch, time, self.width)
        x = x + self.projection(mixed)
        x = x + self.feed(self.norm2(x))
        return self.output(x), {"k": k.detach(), "v": v.detach()}


class LoRAHead(nn.Module):
    def __init__(self, base, rank=2, alpha=2):
        super().__init__()
        self.base = base
        self.rank = rank
        self.scale = alpha / rank
        for parameter in base.parameters():
            parameter.requires_grad_(False)
        self.a = nn.Parameter(torch.randn(base.in_features, rank) * 0.02)
        self.b = nn.Parameter(torch.zeros(rank, base.out_features))

    def forward(self, x):
        return self.base(x) + (x @ self.a @ self.b) * self.scale


def objective(model, inputs, labels):
    logits, _ = model(inputs)
    return F.cross_entropy(logits.reshape(-1, model.vocab), labels.reshape(-1), ignore_index=-100)


torch.manual_seed(31)
base = TinyDecoder()
full = TinyDecoder()
adapted = TinyDecoder()
full.load_state_dict(base.state_dict())
adapted.load_state_dict(base.state_dict())
assert all(torch.equal(a, b) for a, b in zip(full.parameters(), adapted.parameters()))
```

**Expected:** all initial base parameters equal.

### Example B: Install an output-head adapter

ZeroB preserves the original function. The trainable count follows \(32\cdot 2+2\cdot 16\), which is specific to this output-head placement.

```python
for p in adapted.parameters():
    p.requires_grad_(False)
adapted.output = LoRAHead(adapted.output, rank=2, alpha=2)
sequence = torch.tensor([[1, 2, 5, 3], [1, 4, 6, 3]])
inputs = sequence[:, :-1]
labels = sequence[:, 1:].clone()
labels[:, 0] = -100
assert sum(p.numel() for p in adapted.parameters() if p.requires_grad) == 96
with torch.no_grad():
    a, _ = base(inputs)
    b, _ = adapted(inputs)
    torch.testing.assert_close(a, b, atol=1e-6, rtol=0)
```

**Expected:** 96 trainable adapter entries; initial logits match base.

### Example C: Train both candidates under fixed budgets

The rates are declared fixture settings, not tuned on the holdout. Equal step counts do not imply equal compute or equal optimization difficulty, so resource claims require measurement.

```python
frozen = {name: p.detach().clone() for name, p in adapted.named_parameters() if not p.requires_grad}
curves = {}
for name, model, rate in [("full", full, 0.01), ("adapter", adapted, 0.03)]:
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=rate)
    curve = []
    for _ in range(20):
        opt.zero_grad(set_to_none=True)
        loss = objective(model, inputs, labels)
        curve.append(loss.item())
        loss.backward()
        opt.step()
    curves[name] = curve
    assert np.isfinite(curve).all() and curve[-1] < curve[0]
```

**Expected:** both training losses decrease; all logged values finite.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: all initial base parameters equal. adapter 96 entries; 20 updates each; scope literal-token task. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Clone one base into two candidates.** Create a seed 31 decoder and copy its state into full and adapted candidates.
   **Expected:** all initial base parameters equal.
   **Verify:** Save the assertion results for exercise 1, including all initial base parameters equal.

2. **Install an output-head adapter.** Freeze the adapted model, replace its output layer with rank 2LoRA, and compare initial logits.
   **Expected:** 96 trainable adapter entries; initial logits match base.
   **Verify:** Save the assertion results for exercise 2, including 96 trainable adapter entries; initial logits match base.

3. **Train both candidates under fixed budgets.** Run 20 full-SFT updates at.01 and 20 adapter updates at.03 on the same masked batch.
   **Expected:** both training losses decrease; all logged values finite.
   **Verify:** Save the assertion results for exercise 3, including both training losses decrease; all logged values finite.

4. **Prove base preservation.** Compare every frozen adapted-model parameter against its saved copy.
   **Expected:** all frozen tensors exactly equal.
   **Verify:** Save the assertion results for exercise 4, including all frozen tensors exactly equal.

5. **Compare a frozen held-out task.** Evaluate prompt[7, 2] with answer[5, 3] for both candidates using the same mask.
   **Expected:** two finite held-out losses; no predetermined winner.
   **Verify:** Save the assertion results for exercise 5, including two finite held-out losses; no predetermined winner.

6. **Record comparison limits.** Build a report with trainable counts, update budgets, target module and task scope.
   **Expected:** adapter 96 entries; 20 updates each; scope literal-token task.
   **Verify:** Save the assertion results for exercise 6, including adapter 96 entries; 20 updates each; scope literal-token task.

## Common pitfalls and diagnosis

If initial logits differ, inspect state copying, adapter zero initialization, scale and model mode before training. If frozen values change, inspect explicit assignments and optimizer membership. If a model has buffers, include them in state checks rather than assuming parameter equality covers everything.

If one candidate wins the tiny held-out loss, preserve the fixed learning-rate policies and narrow task scope in the report. If resource claims follow only from 96 versus 10464 parameters, request actual allocation and timing evidence. If output-head adaptation fails, inspect whether the hidden representation contains the distinction the task requires.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Controlled adaptation comparison, Target module, Frozen-state proof using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-017` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [LoRA](https://arxiv.org/abs/2106.09685), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-018, Compare full and adapter fine-tuning on frozen tasks.
Read courses/llm-applied/guides/llm-applied-018.md and courses/llm-applied/lessons/llm-applied-018.py. Direct prerequisites: `llm-applied-017`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

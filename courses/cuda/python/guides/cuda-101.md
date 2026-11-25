# cuda-101: LLM training, fine-tuning and GPU memory

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-094`, `cuda-099`, `cuda-100`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Count low-rank parameters.
- Include base storage.
- Inspect optimizer membership.
- Compare sequence-length budgets.
- Design tiny offline training.
- Define held-out evaluation.

## Mechanism and vocabulary

Full fine-tuning updates all selected model parameters. Adapter methods train additional small structures while retaining the base weights. Low-rank updates factor a matrix update into two thinner matrices, reducing trainable parameter count, but the base model still occupies memory and activations still flow through it. Optimizer membership should match the intended trainable set exactly.

Sequence length, padding, batch size, precision, saved activations and optimizer state can dominate different workloads. Build a tiny transformer locally with synthetic tokens before considering downloads. Compare full and adapter training on a held-out synthetic task with equal data accounting. Parameter efficiency is not a guarantee of lower total runtime memory or better quality. Both PyTorch and TensorFlow lanes should report their actual variable census and optimizer state.

## Fine-tuning choices and what remains resident

For a dense weight matrix \(W\in\mathbb R^{m\times n}\), a low-rank update can be written \(\Delta W=AB\), where \(A\) has shape \((m,r)\) and \(B\) has shape \((r,n)\). The trainable update contains \(r(m+n)\) parameters instead of \(mn\). Rank controls the update's representational capacity as well as its parameter count; a smaller rank is a modeling decision that needs validation.

Freezing \(W\) does not remove the forward multiplication by \(W\). Inputs still traverse the base model, and activations may still be needed to train adapters at earlier or later layers. Optimizer state for the frozen weights can disappear when those weights are genuinely excluded from optimization, but the weights themselves remain resident unless an explicit offload or quantization scheme changes their storage. Count these categories separately.

The paired framework examples intentionally use a tiny low-rank matrix rather than downloading a model. The base is an identity matrix, one adapter factor is small and the other starts at zero. The zero update preserves the base function initially. Gradients for the two factors can differ at that initialization, so verify actual gradients instead of assuming both must change on the first step. Then connect this mechanism to attention projection matrices in the existing transformer curriculum.

A complete adaptation study defines the target task, training examples, held-out evaluation, trainable-variable list, optimizer membership, precision policy, sequence/batch cap, checkpoint and rollback. Subject-matter factual knowledge is not guaranteed by lowering training loss: evaluate whether answers use the intended domain evidence and compare a retrieval baseline where appropriate. Parameter-efficient tuning, RAG and prompt design solve overlapping but distinct problems. The GPU lesson supplies resource and training mechanics, while the applied-LLM route supplies grounded-answer and task evaluation design.


### Key terms

- **Full fine-tuning:** Updating every model parameter, which needs gradients and optimizer state for all of them.
- **Adapter:** A small trainable module added to a frozen base model.
- **Low-rank adaptation (LoRA):** Learning a weight update as the product of two small matrices added to a frozen weight.
- **Trainable parameter count:** The number of parameters that receive gradients, which sets gradient and optimizer memory.
- **Optimizer membership:** The set of parameters passed to the optimizer; frozen parameters should be excluded.

## Worked examples

### Worked example 1

A 1024 by 1024 matrix has 1,048,576 parameters. A rank 8 update uses \(8(1024+1024)=16{,}384\) trainable parameters while the original matrix remains present.

### Worked example 2

Freezing the base matrix removes its gradient and optimizer-update requirement under the chosen implementation, but downstream training can still need intermediate activations.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-101_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-101_cpu.py
```

```python
rows, cols, rank = 1024, 1024, 8
base = rows * cols
adapter = rank * (rows + cols)
assert base == 1048576 and adapter == 16384
assert base + adapter > base
print("CPU adapter ledger:", base, adapter, "parameters")
```

**Expected observation:** Base 1,048,576 and adapter 16,384 parameters.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `rows` | `1024` |
| `cols` | `1024` |
| `rank` | `8` |
| `base` | `1048576` |
| `adapter` | `16384` |

## Equal framework lanes

### PyTorch

Freeze base parameters explicitly and construct the optimizer from intended trainable tensors. The included low-rank matrix example demonstrates storage and trainability separately before any full transformer adaptation.

### TensorFlow

Set base variables nontrainable, track adapter variables and pass the intended gradient-variable pairs to the optimizer. Report all resident variables as well as trainable counts.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-101.md) before opening hints.

### Exercise 1: Count low-rank parameters

**Trap to avoid:** Computing rank times the product of dimensions, `8*1024*1024`, gives eight times the original matrix. That figure would make the adapter larger than the weight it adapts, which should immediately signal an error.

### Exercise 2: Include base storage

**Trap to avoid:** Budgeting memory from adapter parameters alone underestimates by the full base model. For this matrix the adapter is about 1.6 percent of the total, so the omitted base dominates the real footprint.

### Exercise 3: Inspect optimizer membership

**Trap to avoid:** Assuming freezing alone excludes parameters from the optimizer can waste memory. Some optimizers skip parameters whose `.grad` is None, but weight decay or other per-parameter bookkeeping may still allocate state, so membership should be explicit rather than implied.

### Exercise 4: Compare sequence-length budgets

**Trap to avoid:** Assuming adapters make long-sequence fine-tuning cheap confuses parameter savings with activation savings. Gradients must still flow back through the frozen layers to reach adapters in earlier layers, so those activations are kept during the forward pass.

### Exercise 5: Design tiny offline training

**Trap to avoid:** Using a full public model and dataset for a first test risks long downloads and exhausting memory. A failure in that setting is also harder to localize, because data, model size and wiring all vary at once.

### Exercise 6: Define held-out evaluation

**Trap to avoid:** Reporting the training loss as model quality overstates performance. Choosing the rank or learning rate by repeatedly looking at the evaluation set leaks it into tuning in the same way.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Multiply the rank by the sum of the matrix's two dimensions.
2. Add the frozen base matrix to the adapter parameters when estimating storage.
3. List the tensors the optimizer holds and compare that list with the ones you meant to train.
4. Ask how attention intermediates and caches grow when sequence length doubles.
5. Generate synthetic tokens locally and bound the number of steps before training anything.
6. Set aside validation data before fitting and keep it out of tuning decisions.

## Common mistakes and self-check

A common mistake is assuming a parameter-efficient method uses little memory. A rank 8 adapter on a 1024 by 1024 matrix trains 16,384 parameters, but the 1,048,576 base parameters stay in memory and activations still flow through them. Another mistake is building the optimizer over all parameters, which adds state for frozen weights. Fix both by counting the variables and optimizer state each framework actually holds and comparing methods on the same held-out synthetic task.

**Evidence limit:** The reference counts 1,048,576 base and 16,384 adapter parameters. It trains no model, so real memory, quality and runtime differences between full and adapter fine-tuning need the framework lanes on a bounded synthetic task.

1. How does a low-rank update reduce trainable parameters?
2. Does freezing the base remove its memory cost?
3. Why build a tiny transformer with synthetic tokens first?

Answers: [self-check answers](../solutions/cuda-101_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-101: LLM training, fine-tuning and GPU memory.
Read courses/cuda/python/guides/cuda-101.md and courses/cuda/python/lessons/cuda-101.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```

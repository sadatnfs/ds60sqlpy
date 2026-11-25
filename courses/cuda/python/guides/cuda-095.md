# cuda-095: Inference has a different performance contract

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-087`, `cuda-090`, `cuda-092`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Compute throughput.
- Separate per-item cost and request latency.
- Set both PyTorch inference controls.
- Specify TensorFlow training behavior.
- Measure cold start.
- Test an exported signature boundary.

## Mechanism and vocabulary

Inference evaluates a trained model without performing optimizer updates, but framework mode still matters. Dropout and normalization can change behavior between training and evaluation. PyTorch eval and inference_mode address different concerns: module behavior versus autograd bookkeeping. TensorFlow calls need explicit inference behavior where the layer contract uses training, and exported signatures need shape and dtype definitions.

Latency per request, batch throughput, tail latency, cold start and memory are separate metrics. A large batch can improve items per second while making an interactive request wait longer. Measure output materialization when a response must be sent to a CPU client. Include model loading and compilation in a separate cold-start result instead of hiding them in warmup.



### Key terms

- **Evaluation mode:** The `model.eval()` setting that switches layers such as dropout and batch normalization to inference behavior.
- **Inference mode:** A PyTorch context that disables gradient tracking and version counters to reduce inference overhead.
- **Throughput:** Samples or requests completed per unit time, often improved by batching.
- **Request latency:** Time from receiving one request to returning its answer, which batching can increase.
- **Cold start:** The cost of the first request, including loading, compilation and allocation before steady state.

## Worked examples

### Worked example 1

A batch of 32 completes in 8 ms, giving 4000 items per second. That does not imply a single request has 0.25 ms latency when queueing and execution require the whole 8 ms.

### Worked example 2

Dropout randomly removes activations during training but should follow the framework's inference contract at evaluation. Disabling gradients alone does not necessarily switch module training behavior.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-095_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-095_cpu.py
```

```python
batch, seconds = 32, 0.008
throughput = batch / seconds
amortized = seconds / batch
assert throughput == 4000
assert amortized == 0.00025
print("CPU serving model:", throughput, "items/s; batch latency", seconds, "s")
```

**Expected observation:** 4000 items/s with 8 ms batch latency, not 0.25 ms request latency.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `batch` | `32` |
| `seconds` | `0.008` |
| `throughput` | `4000.0` |
| `amortized` | `0.00025` |

## Equal framework lanes

### PyTorch

Use model.eval to select evaluation behavior and torch.inference_mode to avoid autograd work. They solve different problems. Materialize the final output inside response-latency timing.

### TensorFlow

Call relevant layers with training=False and define a SavedModel serving signature for the external deployment route. Check output dtypes/shapes and first-call versus warm behavior.

Lane rules: [framework labs](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Executable framework practice

Run the **PyTorch** and **TensorFlow** variants on CPU first; [lab rules](../../STUDY-GUIDE.md#python-gpu-and-framework-labs).

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-095.md) before opening hints.

### Exercise 1: Compute throughput

**Trap to avoid:** Dividing by the time until the batch was enqueued rather than completed inflates throughput, because GPU work is asynchronous and the enqueue returns almost immediately.

### Exercise 2: Separate per-item cost and request latency

**Trap to avoid:** Reporting 0.25 ms as request latency promises response times that no request experiences, and service level objectives built on it will fail.

### Exercise 3: Set both PyTorch inference controls

**Trap to avoid:** Using only `torch.no_grad()` keeps dropout active, so predictions vary between calls, and batch normalization keeps updating running statistics.

### Exercise 4: Specify TensorFlow training behavior

**Trap to avoid:** Assuming `model.predict` and `model(x)` behave the same in every custom layer is risky when a layer reads `training` differently.

### Exercise 5: Measure cold start

**Trap to avoid:** Averaging cold start into steady-state latency hides a multi-second first response. Autoscaling services start new replicas often, so cold start can affect many users.

### Exercise 6: Test an exported signature boundary

**Trap to avoid:** Letting the runtime cast silently makes accepted inputs ambiguous. A float64 request cast to float32 loses precision without anyone noticing.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Divide the batch size by the completed batch time in seconds.
2. Ask how long a single request in that batch waits from arrival to answer.
3. Name what `eval` changes in module behavior and what `inference_mode` changes in autograd bookkeeping.
4. Find the layers whose call signature accepts a training flag and decide what to pass.
5. Time model loading and the first execution separately from warm requests.
6. Send a shape or dtype the exported signature does not accept and decide what should happen.

## Common mistakes and self-check

A common mistake is treating amortized cost per item as request latency. A batch of 32 that takes 8 ms gives 4000 items per second, but each request still waits the whole 8 ms, not 0.25 ms. Another mistake is disabling gradients and assuming dropout and normalization switched to inference behavior. Fix both by reporting latency, throughput, tail latency, cold start and memory separately, and by setting the framework's evaluation mode explicitly.

**Evidence limit:** The reference computes 4000 items per second and an 8 ms batch latency from given numbers. It runs no model, so queueing, output materialization and cold start must be measured on the serving path.

1. Why can a larger batch hurt an interactive service?
2. Why measure cold start separately?
3. Why include output materialization in latency?

Answers: [self-check answers](../solutions/cuda-095_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-095: Inference has a different performance contract.
Read courses/cuda/python/guides/cuda-095.md and courses/cuda/python/lessons/cuda-095.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```

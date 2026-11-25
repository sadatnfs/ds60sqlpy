# cuda-095: explained solutions

Compare with your [worksheet](../lessons/cuda-095.md) attempt.

## Exercise 1: Compute throughput

Batch divided by completed seconds.

**Approach.** Compute throughput as items divided by completed seconds: 32 items in 0.008 s gives `32 / 0.008 = 4000` items per second.

**Why it is correct here.** Throughput measures how much work finishes per unit of time over a completed batch. The reference asserts `throughput == 4000`, using the time at which the whole batch is done.

**A plausible wrong approach.** Dividing by the time until the batch was enqueued rather than completed inflates throughput, because GPU work is asynchronous and the enqueue returns almost immediately.

**How to verify.** Synchronize before stopping the timer, and confirm the measured items per second times the batch time equals the batch size.

## Exercise 2: Separate per-item cost and request latency

Amortized cost is not latency.

**Approach.** Separate amortized cost from latency: `0.008 / 32 = 0.00025` s is the cost per item averaged over the batch, but each request in the batch waits the whole 8 ms, plus any time spent queuing for the batch to fill.

**Why it is correct here.** A request's latency runs from its arrival to its response. Batching shares the 8 ms of execution among 32 items, yet none of them finishes before the batch completes.

**A plausible wrong approach.** Reporting 0.25 ms as request latency promises response times that no request experiences, and service level objectives built on it will fail.

**How to verify.** Record arrival and completion times per request in a serving test. The minimum latency should be at least the 8 ms batch time.

## Exercise 3: Set both PyTorch inference controls

Use eval plus inference_mode when appropriate.

**Approach.** Call `model.eval()` to switch dropout and batch normalization to inference behavior, and wrap inference in `torch.inference_mode()` to disable gradient tracking.

**Why it is correct here.** `eval()` changes module behavior, while `inference_mode` controls autograd. They are independent switches, so both are needed for correct and efficient inference.

**A plausible wrong approach.** Using only `torch.no_grad()` keeps dropout active, so predictions vary between calls, and batch normalization keeps updating running statistics.

**How to verify.** Run the same input twice with dropout in the model: outputs must be identical after `eval()` and may differ without it.

## Exercise 4: Specify TensorFlow training behavior

Pass training=False for relevant calls.

**Approach.** In TensorFlow pass `training=False` when calling the Keras model for inference, which controls dropout and batch normalization behavior.

**Why it is correct here.** Keras layers read the `training` argument to choose behavior. Calling `model(x)` directly in custom code may default to a mode that does not match evaluation.

**A plausible wrong approach.** Assuming `model.predict` and `model(x)` behave the same in every custom layer is risky when a layer reads `training` differently.

**How to verify.** Compare outputs of `model(x, training=False)` across repeated calls; they must be identical when dropout is present.

## Exercise 5: Measure cold start

Include load and first execution separately.

**Approach.** Measure cold start as separate phases: process start and model load, first execution including any compilation or algorithm search, then steady-state execution.

**Why it is correct here.** First requests after deployment pay one-time costs. Separating phases shows whether a slow first response comes from loading weights or from first-call compilation.

**A plausible wrong approach.** Averaging cold start into steady-state latency hides a multi-second first response. Autoscaling services start new replicas often, so cold start can affect many users.

**How to verify.** Record a timestamp after each phase in a fresh process and report each phase separately.

## Exercise 6: Test an exported signature boundary

Reject unsupported shape or dtype explicitly.

**Approach.** Test the exported signature: send an input with an unsupported shape or dtype, such as float64 when the signature declares float32, and confirm a clear rejection.

**Why it is correct here.** The exported model has a fixed contract. Explicit rejection is better than silent casting, which can change numerical behavior.

**A plausible wrong approach.** Letting the runtime cast silently makes accepted inputs ambiguous. A float64 request cast to float32 loses precision without anyone noticing.

**How to verify.** Write tests for one valid and two invalid inputs and assert the error messages name the expected signature.

## Self-check answers

1. **Why can a larger batch hurt an interactive service?** It raises throughput but makes each request wait for the whole batch, increasing latency.

2. **Why measure cold start separately?** Loading and compiling the model happen once and would distort warm request timings if hidden in warmup.

3. **Why include output materialization in latency?** A response for a CPU client is not finished until results are copied back and serialized.

## Reference observation

4000 items/s with 8 ms batch latency, not 0.25 ms request latency.

Asserted by `courses/cuda/python/references/cuda-095_cpu.py`.

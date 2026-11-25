# cuda-087: explained solutions

Compare with your [worksheet](../lessons/cuda-087.md) attempt.

## Exercise 1: Derive the scalar gradient

The mean derivative is average of 2*x*(w*x-y).

**Approach.** Differentiate the mean squared error with respect to the scalar weight: the derivative is the average of `2*x*(w*x - y)`. At `w = 0` the two terms are `2*1*(0-2) = -4` and `2*2*(0-4) = -16`, so the mean gradient is -10.

**Why it is correct here.** The loss is the average of `(w*x - y)**2` over the batch, and the chain rule gives `2*(w*x - y)*x` per example. Averaging matches the mean reduction used for the loss, which is 10 here from `(4 + 16)/2`.

**A plausible wrong approach.** Dropping the factor 2 from the derivative, a common slip when writing it by hand, gives -5 and a half-size update. Autograd would then disagree with the hand derivation.

**How to verify.** Run the reference, which asserts `loss == 10` and `grad == -10`. In PyTorch, call `loss.backward()` on a tensor `w` with `requires_grad=True` and check `w.grad` equals -10.

## Exercise 2: Calculate the update

Weight becomes 1.

**Approach.** Apply plain SGD with learning rate 0.1: `w = 0 - 0.1*(-10) = 1`.

**Why it is correct here.** SGD subtracts the learning rate times the gradient. A negative gradient means increasing `w` lowers the loss, and the data satisfy `y = 2*x`, so moving from 0 toward 2 is the right direction.

**A plausible wrong approach.** Adding the gradient instead of subtracting it gives `w = -1`, which raises the loss to `((-1-2)**2 + (-2-4)**2)/2 = 22.5`. The sign error is easy to miss when only the update size is checked.

**How to verify.** The reference asserts `w == 1` after the update. In a framework, compare the parameter after `optimizer.step()` with 1 and confirm the recomputed loss drops from 10 to 2.5.

## Exercise 3: Compare sum and mean

Sum scales by batch size.

**Approach.** Repeat the step with a sum loss instead of a mean: the loss becomes 20, the gradient `-4 + -16 = -20`, and the update moves `w` to 2.

**Why it is correct here.** A sum reduction scales the gradient by the batch size, 2 here, which has the same effect as doubling the learning rate. The two runs are different training procedures.

**A plausible wrong approach.** Comparing a sum-loss run with a mean-loss run and attributing the speed or convergence difference to the GPU confounds hardware with loss normalization.

**How to verify.** Compute both updates and confirm they differ by exactly the batch-size factor. Record the reduction mode in every training comparison.

## Exercise 4: Inspect every tensor device

Include parameters inputs targets and optimizer tensors.

**Approach.** List every tensor involved in the step, including inputs `x`, targets `y`, the parameter `w`, its gradient and any optimizer state such as momentum buffers, and print each one's `.device`.

**Why it is correct here.** All operands of one operation must live on the same device. A target left on the CPU or an optimizer state created before `model.to(device)` produces an error or an unintended copy.

**A plausible wrong approach.** Checking only the model parameters misses inputs and targets, and moving the model after creating the optimizer can leave the optimizer holding stale references in some setups.

**How to verify.** Write a helper that collects devices from all tensors in the step and asserts the set has one element. It should fail when `y` stays on the CPU.

## Exercise 5: Write equal PyTorch and TensorFlow contracts

Use identical data initial state reduction and rate.

**Approach.** Write one contract for both frameworks: the same `x`, `y`, initial `w = 0`, mean reduction, learning rate 0.1 and float32 dtype, then compare the loss, gradient and updated weight.

**Why it is correct here.** PyTorch and TensorFlow use different APIs, but with identical data, initialization and reduction they must produce loss 10, gradient -10 and weight 1 up to float rounding.

**A plausible wrong approach.** Letting each framework use its default initializer or loss reduction makes the numbers differ for reasons unrelated to correctness.

**How to verify.** Assert both frameworks produce 10, -10 and 1 within a small tolerance. A mismatch then points to a contract difference, which can be found field by field.

## Exercise 6: Distinguish correctness and performance

Time only after output and gradient agreement.

**Approach.** Separate correctness from performance: first confirm outputs and gradients agree with the oracle, and only then time the step on the device with synchronization.

**Why it is correct here.** A fast step computing the wrong update is not an improvement. Timing results matter only after the numbers are known to be right.

**A plausible wrong approach.** Reporting a speedup from a run that silently used a sum loss, or ran partly on the CPU, compares different computations.

**How to verify.** Store correctness results next to each timing, and reject any timing whose correctness check is missing or failed.

## Self-check answers

1. **Why derive the gradient by hand before trusting autograd?** A hand derivation gives an independent expected value, so a wrong loss, shape or placement shows up as a mismatch instead of a plausible number.

2. **How do PyTorch and TensorFlow differ in placement idiom?** PyTorch moves tensors and modules to a device explicitly. TensorFlow relies on device scopes, placement rules and tracked variables.

3. **What does a correct one-step update establish?** Bounded correct behavior for that step. It says nothing about model quality or GPU performance.

## Reference observation

Loss 10, gradient -10, new weight 1.

Asserted by `courses/cuda/python/references/cuda-087_cpu.py`.

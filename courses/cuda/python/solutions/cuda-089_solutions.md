# cuda-089: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Build a parameter ledger

Count each actual array and its dtype.

**Approach.** Build a ledger of training state for 1000 float32 parameters: parameters, gradients and two Adam moment arrays, four arrays of `1000*4` bytes, for 16000 bytes total.

**Why it is correct here.** Each tensor that exists during training gets its own line with element count and itemsize. Adam keeps first and second moments per parameter, which doubles state beyond parameters and gradients.

**A plausible wrong approach.** Counting parameters only, 4000 bytes, underestimates training memory by four times for this optimizer.

**How to verify.** The reference asserts `state_bytes == 16000`. In PyTorch, sum `numel()*element_size()` over parameters, gradients and optimizer state and compare.

## Exercise 2: Add activation bytes

Use batch times elements per example times itemsize.

**Approach.** Add saved activations as batch times elements per example times itemsize: `8*128*4 = 4096` bytes for one saved tensor of 128 float32 values per example.

**Why it is correct here.** Autograd saves intermediate values for the backward pass, and their size scales with batch size. The reference adds two such tensors: `16000 + 2*4096 = 24192` bytes.

**A plausible wrong approach.** Ignoring activations because they are temporary misses that they live from forward until backward, which is when memory peaks.

**How to verify.** Assert the 24192 total from the reference, then double the batch to 16 and confirm the activation portion doubles to 8192 bytes per tensor.

## Exercise 3: Separate reserve and live usage

Reserved includes reusable storage.

**Approach.** Distinguish reserved memory from allocated memory: `torch.cuda.memory_allocated` counts bytes held by live tensors, while `memory_reserved` also counts free blocks the caching allocator keeps.

**Why it is correct here.** The allocator keeps freed blocks for reuse to avoid expensive device allocations, so reserved bytes can stay high after tensors are freed.

**A plausible wrong approach.** Reading the reserved number in a monitoring tool and concluding tensors are leaking confuses cache with live usage. Tools such as `nvidia-smi` report the reserved total, so they show this inflated number.

**How to verify.** Allocate and delete a large tensor, then show allocated memory returns to its prior value while reserved memory stays higher.

## Exercise 4: Diagnose a retained graph

Store detached scalar summaries when appropriate.

**Approach.** Diagnose a retained graph: storing `losses.append(loss)` each step keeps each step's autograd graph alive. Store `loss.item()` or `loss.detach()` instead.

**Why it is correct here.** A loss tensor that requires grad references its graph and saved activations. Keeping one per step grows memory linearly with step count, independent of batch size.

**A plausible wrong approach.** Blaming a fixed-size growth per step on fragmentation or the allocator leads to tuning allocator settings that do not fix the reference leak.

**How to verify.** Track allocated memory per step with both versions. The detached version stays flat, while the retained version rises each step.

## Exercise 5: Explain memory growth

It changes allocation policy not required live bytes.

**Approach.** Explain that allowing memory growth in a framework changes how memory is reserved from the device, incrementally rather than all at once, but does not change the bytes the model needs at peak.

**Why it is correct here.** Growth settings affect allocation policy and sharing with other processes. If the peak live bytes exceed the device, growth only delays the out-of-memory error.

**A plausible wrong approach.** Turning growth on to fix an out-of-memory error treats a policy as a capacity increase.

**How to verify.** Compare the peak allocated bytes with growth on and off for the same step. They should match.

## Exercise 6: Design a safe batch-size experiment

Use small fixed upper bounds and stop before exhausting hardware.

**Approach.** Design a batch-size experiment that steps through small fixed sizes such as 8, 16 and 32, records peak memory for each and stops well before the device limit.

**Why it is correct here.** Peak memory grows roughly linearly with batch size, so a few points allow extrapolation. Bounded steps avoid crashing a shared GPU.

**A plausible wrong approach.** Doubling until the program crashes uses an out-of-memory error as the measurement and can disrupt other users.

**How to verify.** Fit peak memory against batch size from the recorded points and check the slope matches the activation ledger.

## Reference observation

State 16000 bytes and activation 4096 bytes for the example.

The reference file is `courses/cuda/python/references/cuda-089_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

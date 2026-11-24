# cuda-103: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute equal-replica average

Average equal contributions.

**Approach.** With two replicas of equal batch size and mean gradients 2 and 4, all-reduce the gradients and divide by the world size: `(2 + 4)/2 = 3`.

**Why it is correct here.** When every replica holds the same number of examples, the mean of replica means equals the mean over all examples. This is why data-parallel training divides the summed gradient by the number of ranks.

**A plausible wrong approach.** Summing gradients without dividing by world size gives 6, which effectively doubles the learning rate whenever another GPU is added, so changing the device count silently changes training dynamics.

**How to verify.** Run a single-device step on the concatenated batch and compare its gradient to the averaged replica gradient. The reference asserts `sum(gradients)/2 == 3.0` for the equal-size case.

## Exercise 2: Handle unequal counts

Weight by examples or use a documented equal-batch policy.

**Approach.** For unequal counts 3 and 1 with gradients 2 and 4, weight by examples: `(3*2 + 1*4)/(3 + 1) = 10/4 = 2.5`, or adopt a documented policy that every rank processes equal-size batches.

**Why it is correct here.** The global sample mean counts each example once. A plain average of replica means treats the rank with one example as if it held three, giving 3 instead of 2.5.

**A plausible wrong approach.** Relying on the default world-size average when the sampler gives the last rank a short batch introduces a small bias every epoch, which is hard to notice because loss still falls.

**How to verify.** The reference asserts `weighted == 2.5` and that the unweighted mean is 3.0. In a framework, all-reduce both the gradient sum and the example count, then divide.

## Exercise 3: Assign rank and device

Use explicit one-process ownership where required.

**Approach.** Assign each process one rank and one device explicitly, such as `torch.cuda.set_device(local_rank)` before creating tensors or the process group, with the launcher supplying `LOCAL_RANK`.

**Why it is correct here.** Collective libraries expect each rank to own one device. Without explicit assignment several processes default to device 0, oversubscribing its memory while the other GPUs sit idle.

**A plausible wrong approach.** Creating the model before setting the device places every replica on GPU 0, and the first out-of-memory error appears far from its cause.

**How to verify.** Have each rank log its rank, local rank and `torch.cuda.current_device()`, and confirm the mapping is one to one across the job.

## Exercise 4: Check complete sample coverage

No unintended omissions or duplication.

**Approach.** Check that the distributed sampler covers every example exactly once per epoch: union the indices each rank processed and compare with the dataset index set.

**Why it is correct here.** Samplers pad or drop examples so that ranks get equal counts. Padding duplicates a few examples and dropping omits some, and either changes the gradient accounting.

**A plausible wrong approach.** Assuming coverage because each rank processed `len(dataset)/world_size` batches ignores padding and the `drop_last` setting.

**How to verify.** Gather index lists from all ranks for one epoch and assert no duplicates and no missing indices, or record the documented padding count if padding is intended.

## Exercise 5: Design collective failure handling

Bound communication and terminate all owned ranks.

**Approach.** Design collective failure handling: set a bounded timeout on process-group operations and make the launcher terminate every rank it started when one fails.

**Why it is correct here.** A rank that crashes leaves the others blocked inside an all-reduce indefinitely. A timeout turns the hang into an error, and owned-process cleanup releases the GPUs.

**A plausible wrong approach.** Letting surviving ranks wait without a timeout keeps the devices occupied by a job that cannot finish, and nobody receives an error to act on.

**How to verify.** Inject a failure by exiting one rank early in a small test, and confirm the others exit with a timeout error within the configured bound.

## Exercise 6: Compare framework distribution contracts

Each framework needs its own integration test.

**Approach.** Compare distribution contracts across frameworks: PyTorch DDP, Horovod, JAX `pmap` and TensorFlow strategies each define gradient reduction, sampler behavior and launch differently.

**Why it is correct here.** Defaults differ, such as whether the gradient is summed or averaged and how uneven final batches are handled, so a result validated under one framework does not transfer.

**A plausible wrong approach.** Porting a training script between frameworks and assuming identical gradients because both are data-parallel skips the place where the semantics actually differ.

**How to verify.** Write an integration test per framework that compares the two-rank gradient with a single-device reference on the same examples.

## Reference observation

Global example-weighted gradient 2.5.

The reference file is `courses/cuda/python/references/cuda-103_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

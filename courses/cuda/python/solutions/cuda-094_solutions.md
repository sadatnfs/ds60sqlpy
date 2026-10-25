# cuda-094: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: List checkpoint fields

Include all state affecting the next update.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **list checkpoint fields** is qualified there.

## Exercise 2: Compute momentum continuation

Carry the previous velocity.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute momentum continuation** is qualified there.

## Exercise 3: Diagnose weights-only restart

The optimizer trajectory changes.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **diagnose weights-only restart** is qualified there.

## Exercise 4: Record sampler position

Persist the next unconsumed example or reproducible sampler state.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **record sampler position** is qualified there.

## Exercise 5: Choose a safe save boundary

Save after a completed consistent optimizer step.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a safe save boundary** is qualified there.

## Exercise 6: Define cross-hardware tolerance

Document numerical agreement rather than universal byte equality.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define cross-hardware tolerance** is qualified there.

## Reference observation

Correct restored update 0.935 differs from weights-only 0.98.

The reference file is `courses/cuda/python/references/cuda-094_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

# cuda-112: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate median speedup

Divide baseline median by candidate median.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate median speedup** is qualified there.

## Exercise 2: Preserve raw observations

Keep samples and conditions.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **preserve raw observations** is qualified there.

## Exercise 3: Check equivalence first

Fail correctness before performance acceptance.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **check equivalence first** is qualified there.

## Exercise 4: Separate cold and warm costs

Report both boundaries.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate cold and warm costs** is qualified there.

## Exercise 5: Write supported platform scope

Name exactly tested hardware and software.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write supported platform scope** is qualified there.

## Exercise 6: Prepare a reproducibility checklist

Include source data commands versions metrics and unresolved limits.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **prepare a reproducibility checklist** is qualified there.

## Reference observation

Synthetic median ratio 1.25; explicitly not a GPU benchmark.

The reference file is `courses/cuda/python/references/cuda-112_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

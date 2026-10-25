# cuda-085: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute complete latency

Include packing and transfer.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute complete latency** is qualified there.

## Exercise 2: List a numerical contract

Specify shape dtype tolerance and edge behavior.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **list a numerical contract** is qualified there.

## Exercise 3: Add temporary memory

Count peak simultaneously live buffers.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **add temporary memory** is qualified there.

## Exercise 4: Identify a maintenance cost

Architecture and compiler changes need requalification.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **identify a maintenance cost** is qualified there.

## Exercise 5: Choose two workload sizes

Use tiny and representative bounded inputs.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose two workload sizes** is qualified there.

## Exercise 6: Write a keep-or-replace decision

Keep the library unless measured benefits justify added obligations.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write a keep-or-replace decision** is qualified there.

## Reference observation

Library 10 and custom 11 modeled milliseconds.

The reference file is `courses/cuda/python/references/cuda-085_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

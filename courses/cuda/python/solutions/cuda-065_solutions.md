# cuda-065: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace the five events

Construction and retrieval belong to the host.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace the five events** is qualified there.

## Exercise 2: Explain why import is insufficient

Import proves only Python resolution.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain why import is insufficient** is qualified there.

## Exercise 3: Change the input to an empty list

The additive identity is zero.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **change the input to an empty list** is qualified there.

## Exercise 4: Find the hidden transfer in scalar printing

Scalar materialization transfers and may synchronize.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find the hidden transfer in scalar printing** is qualified there.

## Exercise 5: Design a residency ledger

Record object, backend, allocation and completion.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a residency ledger** is qualified there.

## Exercise 6: Explain how a CPU fallback must be labeled

Report CPU reference rather than GPU success.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain how a CPU fallback must be labeled** is qualified there.

## Reference observation

CPU reference: 6; every ledger event is CPU.

The reference file is `courses/cuda/python/references/cuda-065_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

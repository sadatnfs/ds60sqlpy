# cuda-073: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Separate host and device statements

Validation and allocation are host work.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate host and device statements** is qualified there.

## Exercise 2: Implement the CPU oracle

Map each input to twice its value.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **implement the CPU oracle** is qualified there.

## Exercise 3: Reject mismatched lengths

Validate before launch.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **reject mismatched lengths** is qualified there.

## Exercise 4: Move an allocation out of a kernel

Pass a preallocated buffer.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **move an allocation out of a kernel** is qualified there.

## Exercise 5: Explain type specialization

Typed compiled code is not arbitrary interpreter execution.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain type specialization** is qualified there.

## Exercise 6: List a prepared toolchain ledger

Record distribution, Python, toolkit, driver and device.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **list a prepared toolchain ledger** is qualified there.

## Reference observation

[2, -4, 6], with empty input accepted by the oracle.

The reference file is `courses/cuda/python/references/cuda-073_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

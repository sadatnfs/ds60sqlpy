# cuda-081: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Distinguish copy and alias

An alias shares storage.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **distinguish copy and alias** is qualified there.

## Exercise 2: Trace owner lifetime

Keep the producer owner alive under the API contract.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace owner lifetime** is qualified there.

## Exercise 3: Describe metadata requirements

Include dtype shape strides device and offset.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **describe metadata requirements** is qualified there.

## Exercise 4: Explain missing autograd edges

Storage protocols do not universally preserve graph semantics.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain missing autograd edges** is qualified there.

## Exercise 5: Name stream readiness evidence

Record the producer event or negotiated stream.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **name stream readiness evidence** is qualified there.

## Exercise 6: Design mutation tests

Change one view and inspect the other without unsafe concurrent writes.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design mutation tests** is qualified there.

## Reference observation

Alias changes to 9 while copied value remains 1.

The reference file is `courses/cuda/python/references/cuda-081_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

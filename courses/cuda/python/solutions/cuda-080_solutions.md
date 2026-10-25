# cuda-080: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify a CPU result

Call it CPU model or simulator.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **classify a CPU result** is qualified there.

## Exercise 2: Construct a race hidden by serialization

Two updates sharing a read value lose one write.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **construct a race hidden by serialization** is qualified there.

## Exercise 3: Name an unsupported feature

Consult the pinned simulator contract.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **name an unsupported feature** is qualified there.

## Exercise 4: Design the validation ladder

Keep stages separate.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design the validation ladder** is qualified there.

## Exercise 5: Choose a tiny debugging input

Use a nonmultiple small enough to hand-trace.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a tiny debugging input** is qualified there.

## Exercise 6: Write an honest evidence label

GPU correctness remains pending until real execution.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write an honest evidence label** is qualified there.

## Reference observation

Serial count 2 versus a possible lost-update count 1.

The reference file is `courses/cuda/python/references/cuda-080_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

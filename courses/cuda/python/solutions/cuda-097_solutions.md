# cuda-097: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Write the operator schema

Name tensor inputs scalar parameters and output.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write the operator schema** is qualified there.

## Exercise 2: Derive output values

Apply affine then clamp.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive output values** is qualified there.

## Exercise 3: Specify aliasing

State whether output shares storage.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify aliasing** is qualified there.

## Exercise 4: Reject unsupported layout

Check before launch or use deliberate packing.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **reject unsupported layout** is qualified there.

## Exercise 5: Compare framework registration mechanisms

Each framework needs its own registered implementation.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare framework registration mechanisms** is qualified there.

## Exercise 6: Define fixed-project build evidence

Record build ABI architecture and real forward tests.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define fixed-project build evidence** is qualified there.

## Reference observation

Fused affine-ReLU output [0,1,7].

The reference file is `courses/cuda/python/references/cuda-097_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

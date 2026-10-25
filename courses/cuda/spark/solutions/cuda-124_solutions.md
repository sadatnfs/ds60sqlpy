# cuda-124: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Classify four APIs

Name SQL UDF pandas-style and local GPU dataframe surfaces.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **classify four APIs** is qualified there.

## Exercise 2: Replace an equivalent simple UDF

Use a built-in expression if null/type semantics match.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **replace an equivalent simple UDF** is qualified there.

## Exercise 3: Explain Arrow limits

Interchange format is not an execution device.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain Arrow limits** is qualified there.

## Exercise 4: Define GPU-aware UDF ownership

Record assigned device batches and cleanup.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define GPU-aware UDF ownership** is qualified there.

## Exercise 5: Distinguish SQL and ML acceleration

They are separate integrations.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **distinguish SQL and ML acceleration** is qualified there.

## Exercise 6: Design quality parity tests

Use same split target metric and preprocessing.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design quality parity tests** is qualified there.

## Reference observation

Null-preserving expression produces [2, None,6].

The reference file is `courses/cuda/spark/references/cuda-124_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

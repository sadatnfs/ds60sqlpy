# cuda-118: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count fixed-width payload

Rows times element width.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count fixed-width payload** is qualified there.

## Exercise 2: Count validity bytes

Ceiling rows divided by eight.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count validity bytes** is qualified there.

## Exercise 3: Explain string offsets

Offsets identify boundaries in character data.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain string offsets** is qualified there.

## Exercise 4: Locate row-column transitions

Inspect the physical plan.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **locate row-column transitions** is qualified there.

## Exercise 5: Budget transfer payload

Include values masks offsets and temporary copies.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **budget transfer payload** is qualified there.

## Exercise 6: Design a conversion parity test

Compare schema row identity nulls and values.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a conversion parity test** is qualified there.

## Reference observation

Fixed payload 8000 bytes, nine-row mask 2 bytes, string characters 7 bytes.

The reference file is `courses/cuda/spark/references/cuda-118_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

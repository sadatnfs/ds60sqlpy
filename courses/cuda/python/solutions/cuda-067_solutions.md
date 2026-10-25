# cuda-067: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count bytes for ten iterations

The round-trip version moves 20 B.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count bytes for ten iterations** is qualified there.

## Exercise 2: Model a batched transfer

Batch submission reduces fixed cost not payload.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **model a batched transfer** is qualified there.

## Exercise 3: Find premature source reuse

Wait on the copy event before overwrite.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find premature source reuse** is qualified there.

## Exercise 4: Explain pinned-memory lifetime

Keep owner alive until completion.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain pinned-memory lifetime** is qualified there.

## Exercise 5: Design an end-to-end timer

Start before preparation and stop after host output.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design an end-to-end timer** is qualified there.

## Exercise 6: Identify an intentionally CPU-friendly workload

Tiny one-off arrays can favor CPU.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **identify an intentionally CPU-friendly workload** is qualified there.

## Reference observation

81920 versus 8192 modeled bytes; these are not measured timings.

The reference file is `courses/cuda/python/references/cuda-067_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

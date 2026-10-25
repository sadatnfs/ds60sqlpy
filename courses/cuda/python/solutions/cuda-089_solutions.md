# cuda-089: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Build a parameter ledger

Count each actual array and its dtype.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **build a parameter ledger** is qualified there.

## Exercise 2: Add activation bytes

Use batch times elements per example times itemsize.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **add activation bytes** is qualified there.

## Exercise 3: Separate reserve and live usage

Reserved includes reusable storage.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate reserve and live usage** is qualified there.

## Exercise 4: Diagnose a retained graph

Store detached scalar summaries when appropriate.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **diagnose a retained graph** is qualified there.

## Exercise 5: Explain memory growth

It changes allocation policy not required live bytes.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain memory growth** is qualified there.

## Exercise 6: Design a safe batch-size experiment

Use small fixed upper bounds and stop before exhausting hardware.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a safe batch-size experiment** is qualified there.

## Reference observation

State 16000 bytes and activation 4096 bytes for the example.

The reference file is `courses/cuda/python/references/cuda-089_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

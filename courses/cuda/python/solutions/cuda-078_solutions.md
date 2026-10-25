# cuda-078: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace a lost update

Two readers can overwrite one another.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace a lost update** is qualified there.

## Exercise 2: Compute a skewed histogram

Six zeros yield count 6 in bin 0.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute a skewed histogram** is qualified there.

## Exercise 3: Merge partials

Add corresponding bins.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **merge partials** is qualified there.

## Exercise 4: Count private storage

Partials times bins times counter width.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count private storage** is qualified there.

## Exercise 5: Explain floating atomic order

Atomicity does not fix addition order.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain floating atomic order** is qualified there.

## Exercise 6: Specify completion before reading

Wait for all updates and merges before host retrieval.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify completion before reading** is qualified there.

## Reference observation

Histogram bins [2,1,3].

The reference file is `courses/cuda/python/references/cuda-078_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

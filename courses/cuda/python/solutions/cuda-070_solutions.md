# cuda-070: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute live and reserved totals

Free pool blocks are reserved but not live.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute live and reserved totals** is qualified there.

## Exercise 2: Reuse a free block

Equal-sized reuse need not grow reserve.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **reuse a free block** is qualified there.

## Exercise 3: Diagnose a retained-output list

Drop unneeded owners and detached summaries.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **diagnose a retained-output list** is qualified there.

## Exercise 4: Explain why cache clearing is insufficient

Live objects still require storage.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain why cache clearing is insufficient** is qualified there.

## Exercise 5: Design bounded snapshots

Record before and after fixed small steps.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design bounded snapshots** is qualified there.

## Exercise 6: Separate host RAM and VRAM

Container host-memory limits do not generally cap VRAM.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate host RAM and VRAM** is qualified there.

## Reference observation

Live 1024, reserved 1024, retained-output example 4096 bytes.

The reference file is `courses/cuda/python/references/cuda-070_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

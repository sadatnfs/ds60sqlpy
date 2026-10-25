# cuda-102: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive cache bytes

Multiply two for keys and values then all dimensions and width.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive cache bytes** is qualified there.

## Exercise 2: Double the sequence

Cache grows linearly in stored positions.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **double the sequence** is qualified there.

## Exercise 3: Distinguish query and KV heads

Use the model actual KV layout.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **distinguish query and KV heads** is qualified there.

## Exercise 4: Compare cached logits

Compare each bounded step within tolerance.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare cached logits** is qualified there.

## Exercise 5: Separate prefill and decode timing

They stress different operation shapes.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate prefill and decode timing** is qualified there.

## Exercise 6: Label fake versus real quantization

A rounding simulation is not a deployed quantized kernel.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **label fake versus real quantization** is qualified there.

## Reference observation

4096 bytes, doubling to 8192 at twice the sequence length.

The reference file is `courses/cuda/python/references/cuda-102_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

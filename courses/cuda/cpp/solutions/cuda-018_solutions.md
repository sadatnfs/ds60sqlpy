# cuda-018: explanatory solutions

## Mechanism review

Matrix multiplication contracts a shared dimension: an m-by-k matrix A times a k-by-n matrix B produces an m-by-n matrix C. One simple CUDA thread owns one output coordinate and loops across k. Row-major A uses row*k+inner; row-major B uses inner*n+column. The output uses row*n+column. This deliberately simple kernel rereads data and serves as an understandable correctness baseline. Accumulation type and tolerance are part of its specification. Distinct entries and rectangular shapes reveal layout errors better than square all-ones inputs.

The separate [CPU reference](../references/cuda-018_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Multiply \([[1,2,3],[4,5,6]]\) by \([[1,2],[0,1],[2,0]]\). The output is \([[7,4],[16,13]]\). Entry (1,0) is \(4\times 1+5\times 0+6\times 2=16\). Explicitly name every dimension before translating the three scalar indices into flat offsets.

**Approach:** Name m = 2, k = 3, n = 2, then compute each C[r][c] as a sum over k.

**Why it is correct:** Entry (1, 0) pairs row 1 of A with column 0 of B: 4 + 0 + 12 = 16.

**A plausible wrong approach:** Indexing B as B[c][k] uses rows of B instead of columns and gives wrong entries.

**How to verify:** The reference asserts C == [[7, 4], [16, 13]].

## Exercise 2

Multiplying by an identity matrix preserves input, but that test alone can miss some errors. A 3-by-5 times 5-by-2 case exercises tails and asymmetric dimensions. If \(\mathrm{k}=0\), define the sum of zero products as zero and decide how the host handles the empty inputs without invalid launches.

**Approach:** Add a 3-by-5 times 5-by-2 fixture with distinct values beside the identity test.

**Why it is correct:** Unequal dimensions catch swapped strides that a square identity case tolerates.

**A plausible wrong approach:** Relying on identity multiplication lets an implementation that transposes B still pass.

**How to verify:** Compare every entry of the 3-by-2 output with the host triple loop.

## Exercise 3

\(1\times 2+2\times 1+3\times 0=4\). The summation axis is k, not the output column axis.

**Approach:** Sum over k for row 0 and column 1: 1 * 2 + 2 * 1 + 3 * 0.

**Why it is correct:** Column 1 of B is [2, 1, 0], giving 4.

**A plausible wrong approach:** Summing across output columns instead of k adds unrelated products.

**How to verify:** Check that C[0][1] in the reference output is 4.

## Exercise 4

Use unequal m and n with unique values, such as the 2-by-3 times 3-by-2 worked case plus a 3-by-5 times 5-by-2 fixture.

**Approach:** Add a case with m and n different and unique values in every cell.

**Why it is correct:** Swapped m and n changes output shape, so a 2-by-3 times 3-by-2 test exposes it.

**A plausible wrong approach:** Adding more square tests of other sizes never distinguishes m from n.

**How to verify:** Run the asymmetric fixture and confirm output shape 2 by 2 and values match.

## Exercise 5

The output has no elements and the host can return without launching a grid.

**Approach:** Return an empty output before computing any grid when m or n is zero.

**Why it is correct:** No outputs exist, so no thread has work, and a zero grid is invalid.

**A plausible wrong approach:** Launching with ceil(0 / 16) blocks still produces an invalid configuration.

**How to verify:** Call with m = 0 and assert an empty output and no launch.

## Exercise 6

There are 12 products and associated accumulation operations, conventionally about 24 FLOPs. State whether initialization additions are counted.

**Approach:** Count m * n * k = 12 multiplies and roughly as many adds, about 24 FLOPs.

**Why it is correct:** Each output needs k products and k accumulations into the running sum.

**A plausible wrong approach:** Counting only m * n = 4 outputs understates work by the factor k.

**How to verify:** Compute 2 * 2 * 3 * 2 = 24 and state whether initial adds are counted.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-018_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

There are 12 products and associated accumulation operations, conventionally about 24 FLOPs. State whether initialization additions are counted.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.

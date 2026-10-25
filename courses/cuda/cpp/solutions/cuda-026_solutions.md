# cuda-026: explanatory solutions

## Mechanism review

Compute Sanitizer provides several checks with different scopes. Memcheck investigates invalid and misaligned memory accesses; racecheck investigates shared-memory hazards; initcheck investigates uninitialized global-memory reads; synccheck investigates invalid synchronization use. Their observations complement mathematical tests. Instrumentation can be expensive and can change timing, so sanitizer runs are not performance samples. An automated command should select a nonzero error-exitcode, because a tool diagnostic must make the check fail even if the application itself returns success. Never conclude that one clean run proves race freedom for every input or validates unsupported global protocols.

The separate [CPU reference](../references/cuda-026_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For an array of four elements, valid indices are 0 through 3. A kernel that accesses index four has an off-by-one defect even if the returned allocation happens to contain readable bytes nearby. Memcheck is an appropriate additional diagnostic, while a CPU bounds model pinpoints the invalid logical access without a GPU.

## Exercise 2

A consumer reads shared tile\([2]\) before its producer writes. Racecheck can add evidence about that hazard. Replacing the missing barrier with a host sleep does not establish an ordering relationship between those threads. Repair the dependency and still validate returned numerical values.

## Exercise 3

Initcheck addresses that class; retain ordinary result checks because initialization alone does not prove the formula is correct.

## Exercise 4

It makes detected tool errors visible to automation through a nonzero status rather than relying on manual log inspection.

## Exercise 5

No. A ragged tail changes participating accesses and possibly synchronization. Include both sizes and additional relevant boundaries.

## Exercise 6

Confirm the intended failing fixture diagnoses the old problem, run the corrected checker, validate normal/tail outputs and benchmark separately without instrumentation.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-026_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Confirm the intended failing fixture diagnoses the old problem, run the corrected checker, validate normal/tail outputs and benchmark separately without instrumentation.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.

# cuda-049: explanatory solutions

## Mechanism review

A linear solver seeks x such that A*x approximates b. Factorization usually avoids the unnecessary work and numerical costs of explicitly constructing an inverse. Library status tells whether the requested procedure completed; a residual checks how well the returned vector satisfies the equation. A small residual does not guarantee a small error in x when A is ill-conditioned, meaning small input changes can greatly change the solution. Report both the residual and a conditioning interpretation. Workspace, matrix layout, pivoting and rank assumptions belong to the solver contract rather than being incidental implementation details.

The separate [CPU reference](../references/cuda-049_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For A=\([[3,1],[1,2]]\) and b=\([9,8]\), x=\([2,3]\) gives A*x=\([9,8]\), so residual is zero in this exact fixture. This is a good first layout and status test, but it does not exercise singular or poorly conditioned problems.

## Exercise 2

For A=\([[1,1],[1,1.000001]]\), small changes in the second component of b can produce large changes in the two components of x. The nearly dependent rows provide little independent information. A solver returning numbers cannot remove that uncertainty; inspect conditioning and the problem specification.

## Exercise 3

A*x=\([8,6]\), so b-A*x=\([1,2]\). A successful API status cannot excuse this wrong result.

## Exercise 4

A factorization-based solve generally does less unnecessary work and can use better numerical procedures; an explicit inverse is not required for the stated task.

## Exercise 5

A named failure or alternate documented rank-aware method, never a fabricated successful solution.

## Exercise 6

State rank and scaling assumptions, compare a suitable factorization method and report residual plus uncertainty/conditioning rather than only coefficient values.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-049_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State rank and scaling assumptions, compare a suitable factorization method and report residual plus uncertainty/conditioning rather than only coefficient values.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.

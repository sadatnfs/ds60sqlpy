# cuda-104: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Write three constraints

Use measurable limits with units.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write three constraints** is qualified there.

## Exercise 2: Filter infeasible candidates

Reject memory and quality violations before speed ranking.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **filter infeasible candidates** is qualified there.

## Exercise 3: Choose a bottleneck hypothesis

Tie a change to a trace.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a bottleneck hypothesis** is qualified there.

## Exercise 4: Preserve rollback

Keep the unchanged baseline runnable.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **preserve rollback** is qualified there.

## Exercise 5: Design failure tests

Test bounded invalid inputs and resource refusal.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design failure tests** is qualified there.

## Exercise 6: State evidence gaps

Pending GPU validation must remain visible.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **state evidence gaps** is qualified there.

## Reference observation

Only candidate A satisfies all three constraints.

The reference file is `courses/cuda/python/references/cuda-104_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

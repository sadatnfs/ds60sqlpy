# cuda-125: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Draw scheduler layers

Kubernetes allocates pods and Spark allocates tasks.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **draw scheduler layers** is qualified there.

## Exercise 2: Name ownership boundaries

Use exact cluster namespace labels and job identity.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **name ownership boundaries** is qualified there.

## Exercise 3: Diagnose Pending executors

Read events and resource availability.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **diagnose Pending executors** is qualified there.

## Exercise 4: Verify device visibility

Run a bounded owned executor probe.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **verify device visibility** is qualified there.

## Exercise 5: Design private networking

Keep internal services private.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design private networking** is qualified there.

## Exercise 6: Write scoped cleanup

Delete only resources created for this named lab and preserve requested logs.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write scoped cleanup** is qualified there.

## Reference observation

Only the illustrative GPU node is eligible; no cluster operation occurs.

The reference file is `courses/cuda/spark/references/cuda-125_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.

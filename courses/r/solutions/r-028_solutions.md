# r-028: reference reasoning

Use the [complete reference](r-028_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference uses three tasks while keeping concurrency fixed at two. It compares a structured result with a sequential oracle and independent arithmetic 14,77,8. The RNG comparison changes both schedule policy and task order, then compares by explicit identifier.

A deliberately failed task is propagated through the owning function, exercising ordinary on.exit cleanup. The separate runtime qualification covers forced timeout and descendant reaping; this script does not claim that catching an error or reaching a final marker proves that every external termination path is safe. Small fixtures demonstrate contracts rather than parallel speed.

## Explained practice

### Exercise 1

Predict the squared sums for tasks 1:3 and 4:6.

The results are 14 and 77.

**Expected evidence:** Two known scalar outputs.

### Exercise 2

Add a third deterministic task c(2,2) without increasing the worker count.

Exactly two workers process three tasks and return 14,77,8 in input order.

**Expected evidence:** Three results, two workers.

### Exercise 3

Implement a self-contained task that returns count and squared sum.

Each task returns list(count=length(x),sum_squares=sum(x^2)); the first task has count 3 and squared sum 14.

**Expected evidence:** Structured, serial-equivalent task results.

### Exercise 4

Diagnose assigning the same set.seed value inside every simulation task.

Every task would repeat the same random sequence. Assign distinct task streams and retain task identifiers.

**Expected evidence:** Distinct streams with reproducible task results.

### Exercise 5

Compare static scheduling and reversed load-balanced scheduling.

The per-task random vectors are identical even if the task-to-worker assignment changes.

**Expected evidence:** Equality by task ID.

### Exercise 6

Explain cleanup for an ordinary R error versus a forced deadline.

on.exit stops workers during ordinary unwinding; the prepared supervisor separately terminates and reaps descendants after timeout. Do not catch a task error and replace it with a fabricated numerical success.

**Expected evidence:** Both ownership layers and their limits are stated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.

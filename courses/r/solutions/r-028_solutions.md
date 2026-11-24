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

**Approach:** Compute the results serially with `lapply(tasks, summary_task)` before any worker starts.

**Why it holds here:** 1 plus 4 plus 9 is 14, and 16 plus 25 plus 36 is 77. Knowing these values first means the parallel run is checked against arithmetic, not against itself.

**Tempting mistake:** Squaring the sum instead of summing the squares. That gives 36 and 225, values that look plausible but answer a different question.

**Verify:** `vapply(serial, function(x) x$sum_squares, numeric(1))` returns 14, 77, 8.

### Exercise 2

Add a third deterministic task c(2,2) without increasing the worker count.

Exactly two workers process three tasks and return 14,77,8 in input order.

**Expected evidence:** Three results, two workers.

**Approach:** Append `c(2, 2)` to the task list and keep `makePSOCKcluster(2L, ...)` unchanged.

**Why it holds here:** parLapply splits three tasks across two workers and returns the results in input order, so the new task adds 4 plus 4, which is 8, in third place.

**Tempting mistake:** Setting the worker count to `length(tasks)`. A list of a thousand tasks would then start a thousand R processes; the count belongs to the machine budget, not to the data.

**Verify:** `identical(serial, parallel_result)` returns TRUE, and the sums show 14, 77, 8.

### Exercise 3

Implement a self-contained task that returns count and squared sum.

Each task returns list(count=length(x),sum_squares=sum(x^2)); the first task has count 3 and squared sum 14.

**Expected evidence:** Structured, serial-equivalent task results.

**Approach:** Write `summary_task <- function(x) list(count = length(x), sum_squares = sum(x^2))`, using nothing but its argument.

**Why it holds here:** Each worker is a separate R process started with --vanilla and cannot see the main session's variables. A function that reads only its argument behaves the same serially and in parallel, returning count 3L and 14 for 1:3.

**Tempting mistake:** Printing progress with cat() or appending to a shared file. Worker output does not reach the main console by default, and two workers writing one file can interleave lines.

**Verify:** `parallel_result[[1]]$count` returns 3L, and `parallel_result[[1]]$sum_squares` returns 14.

### Exercise 4

Diagnose assigning the same set.seed value inside every simulation task.

Every task would repeat the same random sequence. Assign distinct task streams and retain task identifiers.

**Expected evidence:** Distinct streams with reproducible task results.

**Approach:** Create one L'Ecuyer-CMRG stream per task with `nextRNGStream()`, store it with the task id, and have each task load its own stream before drawing.

**Why it holds here:** If every task called `set.seed(2026)`, all four would draw the same four normal values, so four replicates would be one replicate repeated and any spread between them would be zero.

**Tempting mistake:** Putting `set.seed(2026)` inside draw_task. The run is reproducible, but the simulations are wrongly identical, and the reference check that tasks 1 and 2 differ would fail.

**Verify:** `identical(random_results$a[[1]]$values, random_results$a[[2]]$values)` returns FALSE.

### Exercise 5

Compare static scheduling and reversed load-balanced scheduling.

The per-task random vectors are identical even if the task-to-worker assignment changes.

**Expected evidence:** Equality by task ID.

**Approach:** Run parLapply on the streams and parLapplyLB on `rev(streams)`, order both results by task id, and compare them.

**Why it holds here:** Each task carries its own stream, so its draws do not depend on which worker runs it or in what order. Ordering by id lines the two runs up again.

**Tempting mistake:** Seeding each worker once and letting tasks draw from the worker's stream. The values then depend on which worker took which task, so load balancing changes the results.

**Verify:** `identical(random_results$a, random_results$b)` returns TRUE after both lists are ordered by id.

### Exercise 6

Explain cleanup for an ordinary R error versus a forced deadline.

on.exit stops workers during ordinary unwinding; the prepared supervisor separately terminates and reaps descendants after timeout. Do not catch a task error and replace it with a fabricated numerical success.

**Expected evidence:** Both ownership layers and their limits are stated.

**Approach:** Rely on `on.exit(parallel::stopCluster(cluster))` for ordinary errors, and on the external supervisor to end and reap worker processes after a forced deadline. Let task errors reach the caller.

**Why it holds here:** The deliberate failure test shows parLapply raising the worker's error in the main session, and on.exit then stops the cluster. A forced kill runs no R code at all, so only the supervisor can clean up then.

**Tempting mistake:** Wrapping each task in tryCatch that returns 0 on error. The results look complete, and any average over them is wrong with no sign of the failure.

**Verify:** The handler returns a message containing "deliberate task failure", which shows the error propagated instead of being replaced.

## What the checks establish

The reference makes 6 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.

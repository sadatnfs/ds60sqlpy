# go-028: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-028_solution.go` implements all six cases.

## Mechanism

A worker pool limits active execution but does not create infinite capacity. Queues, in-flight tasks and result buffers all consume resources. Give each task an identity so completion order can differ from presentation order. A collector can place results by index to produce a deterministic final sequence. The producer owns input closure, workers process tasks, and a joiner closes results after all senders exit. Cancellation and partial failure need an explicit policy rather than silently losing tasks. This example performs bounded integer work and joins every goroutine. It illustrates coordination without claiming that more workers always make a program faster.

A jobs channel carries indexed tasks. Start a bounded number of workers, feed jobs and close input. A WaitGroup tracks workers; close results only after Wait completes. Assign each result to its input index. Reject zero workers before starting the pipeline, otherwise a producer may block forever with no consumer.

## 1. Preserve input order: change one input

Copy worked example 1, change `v, err := parallelSquares([]int{3, 1, 2}, 2)` to `v, err := parallelSquares([]int{4, 1, 2}, 2)` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
v, err := parallelSquares([]int{3, 1, 2}, 2)
check(err == nil && len(v) == 3 && v[0] == 9 && v[1] == 1 && v[2] == 4, "order")
```

**Expected:** The edited run panics with `order` because `err == nil && len(v) == 3 && v[0] == 9 && v[1] == 1 && v[2] == 4` no longer holds.

**Verify:** Restoring `v, err := parallelSquares([]int{3, 1, 2}, 2)` makes the check pass again with the worked observation: the result is 9, 1, 4.

Indices restore presentation order. Channel arrival order is not the input-order contract.

**Approach.** Follow each task's `Index` through the pool: whichever worker squares the edited first value 4 returns `squareTask{0, 16}`, and the collector writes it to `out[0]`.

**Why it holds here.** Results are placed by index, not by arrival, so the output is `[16 1 4]` on every run. Only `v[0] == 9` fails, and the check panics with `order`.

**A plausible wrong approach.** Collecting with `out = append(out, result.Value)` in arrival order. With two workers the order of sends on `results` depends on scheduling, so the output is sometimes `[1 9 4]` and the original check fails on some runs only.

**Verify.** Print `v` and see `[16 1 4]` before the panic. Print `v` in the restored program across repeated runs, including under `go run -race`, and it is always `[9 1 4]`.

## 2. Handle empty input: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(err != nil && len(v) == 0, "empty")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
v, err := parallelSquares(nil, 2)
check(err == nil && len(v) == 0, "empty")
```

**Expected:** The defective run panics with `empty`; after restoring `check(err == nil && len(v) == 0, "empty")`, it returns an empty result and terminates.

**Verify:** The edited check fails with message `empty` for a state that `err == nil && len(v) == 0` accepts.

Every channel reaches its owned closure point even when no jobs exist.

**Approach.** Trace the empty call: the feeder ranges over no items and closes `jobs`, both workers' loops end, `wg.Wait` returns and the closer goroutine closes `results`, so the collector returns `make([]int, 0)` with nil.

**Why it holds here.** The function produced an empty slice and no error, so the edited `err != nil` is false and the check panics with `empty`, even though every goroutine finished.

**A plausible wrong approach.** Having each worker call `close(results)` when its range loop ends. With two workers and no jobs, both exit at once and the second close panics with `close of closed channel`. One goroutine, after `wg.Wait`, must own that close.

**Verify.** Print `len(v), err` and see `0 <nil>`. The restored check passes and the program exits instead of hanging, which shows every channel reached its close.

## 3. Reject absent capacity

Request zero workers.

```go
_, err := parallelSquares([]int{1}, 0)
check(err != nil, "zero workers")
```

**Expected:** The call returns an error immediately.

**Verify:** Your solution must keep `err != nil` true. Control: changing `_, err := parallelSquares([]int{1}, 0)` to `_, err := parallelSquares([]int{1}, 1)` panics with message `zero workers`; revert it.

Validation before goroutine creation prevents a deadlock instead of attempting to recover from it.

**Approach.** Validate `workers` before creating any channel or goroutine and return `workers must be 1 through 8` for 0.

**Why it holds here.** The guard runs first, so the call returns nil and the error without starting the pool, and `err != nil` holds.

**A plausible wrong approach.** Removing the guard and trusting the pool. With zero workers `wg.Wait` returns at once, `results` closes and the call returns `[0]` with a nil error, while the feeder goroutine stays blocked forever on `jobs <-`. The check panics with `zero workers` and the leak goes unnoticed.

**Verify.** Print `err` for 0 and for 9 workers and see `workers must be 1 through 8` both times; 1 and 8 workers return nil.

## 4. Compare serial semantics

Use one and three workers for the same three inputs.

```go
a, e1 := parallelSquares([]int{1, 2, 3}, 1)
b, e2 := parallelSquares([]int{1, 2, 3}, 3)
check(e1 == nil && e2 == nil && slices.Equal(a, b), "same semantics")
```

**Expected:** Both produce the same sequence.

**Verify:** Your solution must keep `e1 == nil && e2 == nil && slices.Equal(a, b)` true. Control: changing `a, e1 := parallelSquares([]int{1, 2, 3}, 1)` to `a, e1 := parallelSquares([]int{2, 2, 3}, 1)` panics with message `same semantics`; revert it.

Scheduling changes while the calculation contract stays fixed. Timing claims require separate measurements.

**Approach.** Run the same input with one worker and with three, then compare the slices element by element with `slices.Equal`.

**Why it holds here.** Indexes fix each result's position, so both calls return `[1 4 9]` no matter how the workers interleave, and `slices.Equal` reports true.

**A plausible wrong approach.** Comparing with `a == b`. Go slices are not comparable, so the program does not compile: `invalid operation: a == b (slice can only be compared to nil)`.

**Verify.** Print `a, b` and see `[1 4 9] [1 4 9]`. Measure timing separately with a benchmark rather than inferring it from this check.

## 5. Retain duplicate tasks

Process 2, 2 and 2.

```go
v, err := parallelSquares([]int{2, 2, 2}, 2)
check(err == nil && len(v) == 3 && v[2] == 4, "duplicates")
```

**Expected:** All three results are retained.

**Verify:** Your solution must keep `err == nil && len(v) == 3 && v[2] == 4` true. Control: changing `v, err := parallelSquares([]int{2, 2, 2}, 2)` to `v, err := parallelSquares([]int{2, 2, 3}, 2)` panics with message `duplicates`; revert it.

Positional task identity avoids accidentally deduplicating legitimate repeated work.

**Approach.** Treat each position as its own task: indexes 0, 1 and 2 each carry the value 2 and each write 4 into their own slot.

**Why it holds here.** Equal values do not merge because identity is the index, so the output has three entries and `v[2]` is 4.

**A plausible wrong approach.** Collecting into `map[int]int` keyed by input value to "remove redundant work". All three tasks share the key 2, the map has one entry, the returned slice has length 1 and the check panics with `duplicates`.

**Verify.** Print `v` and see `[4 4 4]`.

## 6. Transfer idle-worker cleanup

Use four workers for one input of 5.

```go
v, err := parallelSquares([]int{5}, 4)
check(err == nil && len(v) == 1 && v[0] == 25, "idle workers")
```

**Expected:** One result equals 25 and all workers exit.

**Verify:** Your solution must keep `err == nil && len(v) == 1 && v[0] == 25` true. Control: changing `v, err := parallelSquares([]int{5}, 4)` to `v, err := parallelSquares([]int{6}, 4)` panics with message `idle workers`; revert it.

Idle workers stop when input closes. Excess capacity still has an operational cost even when termination is correct.

**Approach.** Start four workers for one item: one worker receives the task, the feeder closes `jobs`, and all four range loops end.

**Why it holds here.** After `close(jobs)` every idle worker's `range jobs` stops, so `wg.Wait` returns, `results` closes and the collector returns `[25]`.

**A plausible wrong approach.** Forgetting `close(jobs)` in the feeder. The idle workers block on `range jobs` forever, `wg.Wait` never returns, `results` is never closed and the runtime reports `fatal error: all goroutines are asleep - deadlock!`.

**Verify.** Print `v` and see `[25]`; the program exits normally, which shows no goroutine is left blocking the collector.

## Transfer after comparison

Adapt the pool to compute `len(word)` for `[]string{"go", "", "worker"}` with two workers, keeping an index on every task. Check the result is 2, 0, 6 in input order, that 9 workers are rejected before any goroutine starts and that empty input returns an empty slice. Explain what a per-worker close of `results` or a missing close of `jobs` would do.

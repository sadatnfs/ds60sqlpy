# go-028: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A worker pool limits active execution but does not create infinite capacity. Queues, in-flight tasks and result buffers all consume resources. Give each task an identity so completion order can differ from presentation order. A collector can place results by index to produce a deterministic final sequence. The producer owns input closure, workers process tasks, and a joiner closes results after all senders exit. Cancellation and partial failure need an explicit policy rather than silently losing tasks. This example performs bounded integer work and joins every goroutine. It illustrates coordination without claiming that more workers always make a program faster.

A jobs channel carries indexed tasks. Start a bounded number of workers, feed jobs and close input. A WaitGroup tracks workers; close results only after Wait completes. Assign each result to its input index. Reject zero workers before starting the pipeline, otherwise a producer may block forever with no consumer.

## 1. Preserve input order

Square 3, 1 and 2 with two workers.

```go
v, err := parallelSquares([]int{3, 1, 2}, 2)
check(err == nil && len(v) == 3 && v[0] == 9 && v[1] == 1 && v[2] == 4, "order")
```

**Expected:** The result is 9, 1, 4.

Indices restore presentation order. Channel arrival order is not the input-order contract.

## 2. Handle empty input

Run the pool on an empty slice.

```go
v, err := parallelSquares(nil, 2)
check(err == nil && len(v) == 0, "empty")
```

**Expected:** It returns an empty result and terminates.

Every channel reaches its owned closure point even when no jobs exist.

## 3. Reject absent capacity

Request zero workers.

```go
_, err := parallelSquares([]int{1}, 0)
check(err != nil, "zero workers")
```

**Expected:** The call returns an error immediately.

Validation before goroutine creation prevents a deadlock instead of attempting to recover from it.

## 4. Compare serial semantics

Use one and three workers for the same three inputs.

```go
a, e1 := parallelSquares([]int{1, 2, 3}, 1)
b, e2 := parallelSquares([]int{1, 2, 3}, 3)
check(e1 == nil && e2 == nil && slices.Equal(a, b), "same semantics")
```

**Expected:** Both produce the same sequence.

Scheduling changes while the calculation contract stays fixed. Timing claims require separate measurements.

## 5. Retain duplicate tasks

Process 2, 2 and 2.

```go
v, err := parallelSquares([]int{2, 2, 2}, 2)
check(err == nil && len(v) == 3 && v[2] == 4, "duplicates")
```

**Expected:** All three results are retained.

Positional task identity avoids accidentally deduplicating legitimate repeated work.

## 6. Transfer idle-worker cleanup

Use four workers for one input of 5.

```go
v, err := parallelSquares([]int{5}, 4)
check(err == nil && len(v) == 1 && v[0] == 25, "idle workers")
```

**Expected:** One result equals 25 and all workers exit.

Idle workers stop when input closes. Excess capacity still has an operational cost even when termination is correct.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

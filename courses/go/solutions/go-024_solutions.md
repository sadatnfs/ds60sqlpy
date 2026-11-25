# go-024: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-024_solution.go` implements all six cases.

## Mechanism

A goroutine is a concurrently scheduled execution of a function. Starting one does not make the caller wait for it, and returning from main ends the program even if other goroutines still have work. Concurrency introduces partial ordering: some events must happen before others, while unrelated scheduling remains unspecified. Use communication or synchronization to establish the relationships required by the algorithm. A sleep is a delay, not proof that another goroutine has completed. Every started goroutine needs an owner responsible for its completion or cancellation, otherwise blocked tasks can leak resources and make shutdown unpredictable.

go function() starts a goroutine. A channel send and receive can transfer a result and establish an ordering relationship. sync.WaitGroup tracks a known set of tasks; Add must happen before a concurrent Wait can conclude. Defer Done inside each task. Do not write a shared ordinary variable concurrently merely because a later print appears to observe the expected value.

## 1. Join a produced result: change one input

Copy worked example 1, change `go func() { result <- 6 * 7 }()` to `go func() { result <- 7 * 7 }()` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
result := make(chan int)
go func() { result <- 6 * 7 }()
check(<-result == 42, "goroutine result")
```

**Expected:** The edited run panics with `goroutine result` because `<-result == 42` no longer holds.

**Verify:** Restoring `go func() { result <- 6 * 7 }()` makes the check pass again with the worked observation: the received value is 42.

The receive waits for the send. The program does not assume the worker has completed merely because enough wall-clock time passed.

## 2. Wait for several tasks: debug a regression

A one-token regression in worked example 2 makes a line read `for i := 1; i < 3; i++ {`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
done := make(chan struct{}, 3)
var wg sync.WaitGroup
for i := 0; i < 3; i++ {
	wg.Add(1)
	go func() { defer wg.Done(); done <- struct{}{} }()
}
wg.Wait()
check(len(done) == 3, "joined tasks")
```

**Expected:** The defective run panics with `joined tasks`; after restoring `for i := 0; i < 3; i++ {`, exactly three completion markers are received.

**Verify:** The failing run shows message `joined tasks`; after the repair `len(done) == 3` holds again.

The buffer avoids blocking completion before the parent reads. WaitGroup joins the tasks; the channel stores inspectable completion evidence.

## 3. Keep state task-local

Have two goroutines compute from explicit arguments.

```go
out := make(chan int, 2)
for _, n := range []int{2, 3} {
	go func(x int) { out <- x * x }(n)
}
a, b := <-out, <-out
check(a+b == 13, "local inputs")
```

**Expected:** The results sum to 13.

**Verify:** Your solution must keep `a+b == 13` true. Control: changing `go func(x int) { out <- x * x }(n)` to `go func(x int) { out <- x + x }(n)` panics with message `local inputs`; revert it.

The order of a and b is unspecified, so the assertion checks an order-independent property. Explicit arguments make each input ownership clear.

## 4. Establish a start boundary

Block a worker on a start channel, then release it.

```go
start := make(chan struct{})
out := make(chan string)
go func() { <-start; out <- "ready" }()
close(start)
check(<-out == "ready", "start boundary")
```

**Expected:** The worker returns ready only after release.

**Verify:** Your solution must keep `<-out == "ready"` true. Control: changing `go func() { <-start; out <- "ready" }()` to `go func() { <-start; out <- "ready!" }()` panics with message `start boundary`; revert it.

Closing a channel can broadcast a one-time event. It does not carry a payload, and ownership must ensure it is closed only once.

## 5. Reject premature completion

Keep a worker blocked behind a start channel and test whether its result is available before release.

```go
start := make(chan struct{})
out := make(chan int)
go func() { <-start; out <- 1 }()
premature := false
select {
case <-out:
	premature = true
default:
}
check(!premature, "premature completion")
close(start)
check(<-out == 1, "released result")
```

**Expected:** The result is unavailable before release and equals 1 afterward.

**Verify:** Your solution must keep `<-out == 1` true. Control: changing `go func() { <-start; out <- 1 }()` to `go func() { <-start; out <- 2 }()` panics with message `released result`; revert it.

The blocked worker cannot send before the start boundary. This negative case rejects the assumption that starting a goroutine means its work has already completed, without relying on a sleep.

## 6. Transfer deterministic aggregation

Collect squares from four workers and sum them in the receiving goroutine.

```go
out := make(chan int, 4)
for _, n := range []int{1, 2, 3, 4} {
	go func(x int) { out <- x * x }(n)
}
sum := 0
for i := 0; i < 4; i++ {
	sum += <-out
}
check(sum == 30, "aggregation")
```

**Expected:** The sum is 30.

**Verify:** Your solution must keep `sum == 30` true. Control: changing `go func(x int) { out <- x * x }(n)` to `go func(x int) { out <- x + x }(n)` panics with message `aggregation`; revert it.

Only the receiver mutates sum, so no mutex is required for that accumulator. Channel result order is irrelevant to integer addition in this bounded example.

## Transfer after comparison

Every concurrent design in later lessons needs an explicit answer to the question: who waits for this goroutine, and how does its result become visible? Channels, WaitGroups, errgroup and contexts are all answers to it. When a controller starts informers or a server starts handlers, trace the join and the shutdown path before trusting the happy path.

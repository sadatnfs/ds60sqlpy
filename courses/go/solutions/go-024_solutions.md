# go-024: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A goroutine is a concurrently scheduled execution of a function. Starting one does not make the caller wait for it, and returning from main ends the program even if other goroutines still have work. Concurrency introduces partial ordering: some events must happen before others, while unrelated scheduling remains unspecified. Use communication or synchronization to establish the relationships required by the algorithm. A sleep is a delay, not proof that another goroutine has completed. Every started goroutine needs an owner responsible for its completion or cancellation, otherwise blocked tasks can leak resources and make shutdown unpredictable.

go function() starts a goroutine. A channel send and receive can transfer a result and establish an ordering relationship. sync.WaitGroup tracks a known set of tasks; Add must happen before a concurrent Wait can conclude. Defer Done inside each task. Do not write a shared ordinary variable concurrently merely because a later print appears to observe the expected value.

## 1. Join a produced result

Start a goroutine computing 6 times 7 and receive its result.

```go
result := make(chan int)
go func() { result <- 6 * 7 }()
check(<-result == 42, "goroutine result")
```

**Expected:** The received value is 42.

The receive waits for the send. The program does not assume the worker has completed merely because enough wall-clock time passed.

## 2. Wait for several tasks

Start three tasks that signal a buffered completion channel and wait for all of them.

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

**Expected:** Exactly three completion markers are received.

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

Only the receiver mutates sum, so no mutex is required for that accumulator. Channel result order is irrelevant to integer addition in this bounded example.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

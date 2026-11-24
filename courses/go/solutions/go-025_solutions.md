# go-025: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A channel connects producers and consumers with typed communication. An unbuffered send completes when a receiver participates; a buffered channel retains values up to its capacity. Buffering changes backpressure, not ownership of referenced objects sent through the channel. Closing means no more values will be sent. Receivers drain buffered values before observing closure. The producer that knows all sending is finished should own close. A receiver normally must not close the channel merely because it is done reading. Sending after close panics. A send or receive on a nil channel blocks forever, and a select skips such a case; closing a nil channel panics.

make(chan int, 2) creates a two-element buffer. value, ok := <-ch distinguishes a delivered value from the zero value after closure. range ch receives until closed and drained. chan<- int restricts a parameter to sending; <-chan int restricts it to receiving. len(ch) is a transient observation rather than a synchronization protocol.

## 1. Drain before iteration ends: change one input

Copy worked example 1 into a scratch pad and change `ch <- 2` to `ch <- 3`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
ch := make(chan int, 2)
ch <- 2
ch <- 3
close(ch)
sum := 0
for v := range ch {
	sum += v
}
check(sum == 5, "drain")
```

**Expected:** The changed run panics with `drain` because `sum == 5` no longer holds. Restoring the original line brings back the worked observation: both values arrive and the sum is 5.

Close does not erase buffered values. Iteration ends after those values have been received.

**Approach.** Trace the edited sends: the buffer of capacity 2 now holds 3 and 3, `close` marks the channel finished, and `range` receives both values before it stops.

**Why it holds here.** Both sends complete without a receiver because the buffer has room for two, and close keeps buffered values, so the sum is 6 and the check `sum == 5` panics with `drain`.

**A plausible wrong approach.** Predicting a deadlock because nothing receives during the sends, or a zero sum because close discards the buffer. Capacity 2 lets both sends finish, and `range` drains buffered values before it observes the close.

**Verify.** Print `sum` and see 6 before the panic. As a separate experiment, delete `close(ch)`: the loop drains both values and then the runtime stops with `fatal error: all goroutines are asleep - deadlock!`.

## 2. Distinguish zero from closed: debug a regression

A regression changed one token in worked example 2, so one line now reads `ch <- 1`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
ch := make(chan int, 1)
ch <- 0
close(ch)
a, okA := <-ch
b, okB := <-ch
check(a == 0 && b == 0 && okA && !okB, "closed presence")
```

**Expected:** Before the repair the program panics with `closed presence`; after it the line reads `ch <- 0` again and the first zero has ok true; the second has ok false.

Value equality cannot distinguish a delivered zero from the post-closure zero. The boolean carries completion information.

**Approach.** Use the two-result receive to read the regressed state: the first receive yields 1 with `okA` true and the second yields the zero value with `okB` false.

**Why it holds here.** The check requires the delivered value to be 0, so 1 fails `a == 0` and panics with `closed presence`. Sending 0 again makes both received values zero while `ok` still separates them.

**A plausible wrong approach.** Testing completion with `b == 0` instead of `okB`. With the original program both `a` and `b` are 0, so value comparison cannot tell a delivered zero from the closed channel's zero.

**Verify.** Print `a, okA, b, okB`: the regression shows `1 true 0 false` and the repair shows `0 true 0 false`.

## 3. Use sender ownership

Run a producer sending 1 and 2 before closing output.

```go
ch := make(chan int)
go produce(ch)
count := 0
for range ch {
	count++
}
check(count == 2, "producer close")
```

**Expected:** The consumer receives exactly two values.

The producer knows all sends are finished. A receiver closing early could race with a later send.

**Approach.** Let `produce` own the channel: it sends 1 and 2 on the unbuffered channel and its deferred `close` runs after the last send, which ends the consumer's `range`.

**Why it holds here.** Each unbuffered send waits for the receive, so both values arrive in order, and the close happens only after the producer has finished sending, so `count` is exactly 2.

**A plausible wrong approach.** Leaving out the `defer close(out)` in `produce`. The consumer receives two values and then waits forever on an open channel with no sender, and the runtime reports `fatal error: all goroutines are asleep - deadlock!`.

**Verify.** Collect the values into a slice and print it to see `[1 2]` with `count` 2. Closing from `main` before the producer finishes instead produces `panic: send on closed channel`.

## 4. Inspect bounded buffering

Fill a channel of capacity two without a receiver.

```go
ch := make(chan int, 2)
ch <- 4
ch <- 5
check(len(ch) == 2 && cap(ch) == 2, "buffer")
<-ch
<-ch
```

**Expected:** Its buffered length is two.

This sequential fixture has an exact count. Concurrent length checks cannot prove a later send will be nonblocking.

**Approach.** Send 4 and 5 into a channel of capacity 2 with no receiver, then read `len` and `cap` before draining.

**Why it holds here.** Two sends fit the buffer, so neither blocks; `len(ch)` reports the two queued values and `cap(ch)` the fixed capacity 2.

**A plausible wrong approach.** Adding a third send `ch <- 6` before the receives. The buffer is full and no goroutine receives, so `main` blocks forever and the run ends with the all goroutines are asleep deadlock error.

**Verify.** Print `len(ch), cap(ch)` before and after the two receives and see `2 2`, then `0 2`.

## 5. Disable a nil select arm

Select between nil and a ready closed channel.

```go
var disabled <-chan int
ready := make(chan struct{})
close(ready)
selected := false
select {
case <-disabled:
	panic("nil selected")
case <-ready:
	selected = true
}
check(selected, "nil arm")
```

**Expected:** Only the ready arm can proceed.

Nil can deliberately disable an unneeded select case. It does not signal completion like a closed channel.

**Approach.** Use a nil receive channel as the disabled arm and a closed `ready` channel as the live one.

**Why it holds here.** A receive from a nil channel never proceeds, so `select` can only choose `<-ready`, which is immediately ready because the channel is closed. `selected` becomes true every run.

**A plausible wrong approach.** Disabling the arm with a closed channel instead of nil. A closed channel is always ready, `select` picks uniformly at random among ready arms, and about half the runs panic with `nil selected`.

**Verify.** Run the case several times and it always passes. In the closed-channel version, repeated runs may succeed or panic with `nil selected` unpredictably.

## 6. Transfer independent message storage

Send a copied slice, then mutate its original.

```go
original := []int{1}
ch := make(chan []int, 1)
ch <- append([]int(nil), original...)
original[0] = 9
received := <-ch
check(received[0] == 1, "copy")
```

**Expected:** The received copy stays 1.

A channel sends the slice descriptor. The explicit copy establishes independent storage before communication.

**Approach.** Copy the slice with `append([]int(nil), original...)` before sending it, then mutate `original`.

**Why it holds here.** The copy has its own backing array, so `original[0] = 9` changes only the original, and the received slice still holds 1.

**A plausible wrong approach.** Sending `original` directly. The channel copies only the slice header, which points at the same backing array, so the later write makes `received[0]` 9 and the check panics with `copy`.

**Verify.** Print `received, original` and see `[1] [9]`; with the direct send the output is `[9] [9]`.

## Transfer after comparison

Write `squares(n int, out chan<- int)` that sends 1, 4, up to n*n and closes `out`, and sum its output with `range`. Check `squares(3)` totals 14, `squares(0)` totals 0 because the range ends at once, and a channel of capacity 3 holds all three values before the consumer starts. Explain which run deadlocks if the producer forgets to close.

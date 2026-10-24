# go-025: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A channel connects producers and consumers with typed communication. An unbuffered send completes when a receiver participates; a buffered channel retains values up to its capacity. Buffering changes backpressure, not ownership of referenced objects sent through the channel. Closing means no more values will be sent. Receivers drain buffered values before observing closure. The producer that knows all sending is finished should own close. A receiver normally must not close the channel merely because it is done reading. Sending after close panics; an operation on a nil channel blocks unless a select chooses another ready case.

make(chan int, 2) creates a two-element buffer. value, ok := <-ch distinguishes a delivered value from the zero value after closure. range ch receives until closed and drained. chan<- int restricts a parameter to sending; <-chan int restricts it to receiving. len(ch) is a transient observation rather than a synchronization protocol.

## 1. Drain before iteration ends

Buffer 2 and 3, close and sum the channel.

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

**Expected:** Both values arrive and the sum is 5.

Close does not erase buffered values. Iteration ends after those values have been received.

## 2. Distinguish zero from closed

Send zero, close, then receive twice with comma-ok.

```go
ch := make(chan int, 1)
ch <- 0
close(ch)
a, okA := <-ch
b, okB := <-ch
check(a == 0 && b == 0 && okA && !okB, "closed presence")
```

**Expected:** The first zero has ok true; the second has ok false.

Value equality cannot distinguish a delivered zero from the post-closure zero. The boolean carries completion information.

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

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

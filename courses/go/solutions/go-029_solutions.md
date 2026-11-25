# go-029: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-029_solution.go` implements all six cases.

## Mechanism

A data race occurs when conflicting concurrent accesses include a write and lack synchronization. A program that prints the desired value once can still race. The memory model specifies ordering guarantees supplied by channels, mutexes and other primitives. Publish initialized state through such a boundary, then keep it immutable or protect future mutations. The race detector observes executed instrumented paths; a clean run is evidence rather than proof about every schedule. Do not intentionally execute racy examples in ordinary references. Prefer a design whose ownership and ordering can be explained before relying on a diagnostic tool.

A channel send synchronizes with its corresponding receive. Closing a channel synchronizes with a receive observing closure. An unlock synchronizes with a later lock on that mutex. atomic.Value can publish immutable snapshots. The ordinary pad has CGO disabled and does not claim race instrumentation; a prepared Linux development project with a compatible C toolchain can run go test -race ./....

## 1. Publish through a channel: change one input

Copy worked example 1, change `go func() { ch <- Published{Count: 3, Ready: true} }()` to `go func() { ch <- Published{Count: 4, Ready: true} }()` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
ch := make(chan Published)
go func() { ch <- Published{Count: 3, Ready: true} }()
v := <-ch
check(v.Ready && v.Count == 3, "publication")
```

**Expected:** The edited run panics with `publication` because `v.Ready && v.Count == 3` no longer holds.

**Verify:** Restoring `go func() { ch <- Published{Count: 3, Ready: true} }()` makes the check pass again with the worked observation: the reader observes count 3 and ready true.

The send and receive establish ordering without a timing guess.

## 2. Publish through closure: debug a regression

A one-token regression in worked example 2 makes a line read `go func() { n = 8; close(done) }()`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
done := make(chan struct{})
n := 0
go func() { n = 7; close(done) }()
<-done
check(n == 7, "close publication")
```

**Expected:** The defective run panics with `close publication`; after restoring `go func() { n = 7; close(done) }()`, the reader observes 7.

**Verify:** The failing run shows message `close publication`; after the repair `n == 7` holds again.

Removing this synchronization would make the ordinary shared variable unsafe. The proof uses ordering, not elapsed time.

## 3. Publish an atomic value

Store a complete record in atomic.Value.

```go
var current atomic.Value
current.Store(Published{Count: 4, Ready: true})
v := current.Load().(Published)
check(v.Count == 4 && v.Ready, "atomic value")
```

**Expected:** The loaded record has count 4.

**Verify:** Your solution must keep `v.Count == 4 && v.Ready` true. Control: changing `current.Store(Published{Count: 4, Ready: true})` to `current.Store(Published{Count: 5, Ready: true})` panics with message `atomic value`; revert it.

Publishing a pointer does not make subsequent unsynchronized target mutation safe. This snapshot has scalar fields.

## 4. Retain a previous snapshot

Load a value, then replace the stored value.

```go
var current atomic.Value
current.Store(Published{Count: 4})
old := current.Load().(Published)
current.Store(Published{Count: 5})
check(old.Count == 4 && current.Load().(Published).Count == 5, "replacement")
```

**Expected:** The old copy remains 4 and the current value is 5.

**Verify:** Your solution must keep `old.Count == 4 && current.Load().(Published).Count == 5` true. Control: changing `current.Store(Published{Count: 4})` to `current.Store(Published{Count: 5})` panics with message `replacement`; revert it.

Value snapshots avoid shared mutable fields only when their contained values also have the intended ownership semantics.

## 5. Copy reference-containing data

Copy a slice before mutating the original.

```go
original := []int{1, 2}
snapshot := append([]int(nil), original...)
original[0] = 9
check(snapshot[0] == 1, "independent data")
```

**Expected:** The snapshot retains its original first element.

**Verify:** Your solution must keep `snapshot[0] == 1` true. Control: changing `original := []int{1, 2}` to `original := []int{2, 2}` panics with message `independent data`; revert it.

Copying can eliminate shared mutable storage. Synchronization instead orders accesses to storage that remains shared.

## 6. Transfer local construction

Build a result string inside a worker and send the completed value.

```go
ch := make(chan string)
go func() { ch <- fmt.Sprintf("ready:%d", 3) }()
check(<-ch == "ready:3", "result")
```

**Expected:** The reader receives `ready:3`.

**Verify:** Your solution must keep `<-ch == "ready:3"` true. Control: changing `go func() { ch <- fmt.Sprintf("ready:%d", 3) }()` to `go func() { ch <- fmt.Sprintf("ready:%d", 4) }()` panics with message `result`; revert it.

Keeping construction state local simplifies the argument compared with exposing several partially updated shared fields.

## Transfer after comparison

Controllers and servers publish state constantly: a cache filled by one goroutine and read by handlers, or configuration reloaded while requests run. Apply the same rule there: build the value completely, publish it through a channel, lock or atomic, and treat it as read-only afterward. Run go test -race in CI so a lucky schedule never stands in for evidence.

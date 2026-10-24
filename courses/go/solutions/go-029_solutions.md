# go-029: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A data race occurs when conflicting concurrent accesses include a write and lack synchronization. A program that prints the desired value once can still race. The memory model specifies ordering guarantees supplied by channels, mutexes and other primitives. Publish initialized state through such a boundary, then keep it immutable or protect future mutations. The race detector observes executed instrumented paths; a clean run is evidence rather than proof about every schedule. Do not intentionally execute racy examples in ordinary references. Prefer a design whose ownership and ordering can be explained before relying on a diagnostic tool.

A channel send synchronizes with its corresponding receive. Closing a channel synchronizes with a receive observing closure. An unlock synchronizes with a later lock on that mutex. atomic.Value can publish immutable snapshots. The ordinary pad has CGO disabled and does not claim race instrumentation; a prepared Linux development project with a compatible C toolchain can run go test -race ./....

## 1. Publish through a channel

Send an initialized record from a goroutine.

```go
ch := make(chan Published)
go func() { ch <- Published{Count: 3, Ready: true} }()
v := <-ch
check(v.Ready && v.Count == 3, "publication")
```

**Expected:** The reader observes count 3 and ready true.

The send and receive establish ordering without a timing guess.

## 2. Publish through closure

Write 7 before closing done, then read after receiving done.

```go
done := make(chan struct{})
n := 0
go func() { n = 7; close(done) }()
<-done
check(n == 7, "close publication")
```

**Expected:** The reader observes 7.

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

Copying can eliminate shared mutable storage. Synchronization instead orders accesses to storage that remains shared.

## 6. Transfer local construction

Build a result string inside a worker and send the completed value.

```go
ch := make(chan string)
go func() { ch <- fmt.Sprintf("ready:%d", 3) }()
check(<-ch == "ready:3", "result")
```

**Expected:** The reader receives ready:3.

Keeping construction state local simplifies the argument compared with exposing several partially updated shared fields.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

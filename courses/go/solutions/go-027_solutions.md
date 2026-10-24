# go-027: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A mutex protects a state invariant across several operations. Every relevant access must follow the same protocol: locking writes while reading without synchronization can still race. Atomic operations protect specific values and ordering relationships, but do not automatically make a multi-field transaction atomic. Prefer a mutex for a compound invariant that must be inspected and changed together. Never copy a mutex after use. Keep critical sections small, avoid calling unknown callbacks while holding a lock, and define lock ordering when several locks are unavoidable. A correct observed count is not by itself proof of correct synchronization.

sync.Mutex uses Lock and Unlock; defer Unlock after acquisition handles early returns. atomic.Int64 supplies typed Load, Store and Add. sync.Once runs one initialization function. Keep synchronized state in a pointer-owned holder so it is not copied accidentally. count++ on an ordinary shared integer is a read-modify-write sequence, not an atomic operation.

## 1. Protect a concurrent count

Run four workers doing 100 protected increments each.

```go
c := &LockedCount{}
var wg sync.WaitGroup
for i := 0; i < 4; i++ {
	wg.Add(1)
	go func() {
		defer wg.Done()
		for j := 0; j < 100; j++ {
			c.Inc()
		}
	}()
}
wg.Wait()
check(c.Value() == 400, "count")
```

**Expected:** The joined final count is 400.

Reads and writes use the same lock. The join establishes task completion before inspection.

## 2. Use a typed atomic

Add 3 and 4 through atomic.Int64.

```go
var n atomic.Int64
n.Add(3)
n.Add(4)
check(n.Load() == 7, "atomic")
```

**Expected:** Load returns 7.

Use the atomic access API consistently. Mixing it with ordinary conflicting accesses undermines the protocol.

## 3. Protect a pair relationship

Transfer 3 between two balances initially 5 and 5.

```go
p := &Pair{A: 5, B: 5}
p.Transfer(3)
a, b := p.Snapshot()
check(a == 2 && b == 8 && a+b == 10, "pair")
```

**Expected:** The balances become 2 and 8; their sum remains 10.

One lock protects both fields. Independent updates could expose an intermediate state with the wrong total.

## 4. Initialize once

Call the same sync.Once initializer three times.

```go
var once sync.Once
n := 0
for i := 0; i < 3; i++ {
	once.Do(func() { n++ })
}
check(n == 1, "once")
```

**Expected:** Its body runs once.

Once is not a retry mechanism. Fallible initialization requiring retries needs a separately designed state machine.

## 5. Reject a stale atomic expectation

Perform compare-and-swap twice using the original expected value.

```go
var n atomic.Int64
n.Store(2)
check(n.CompareAndSwap(2, 3), "CAS")
check(!n.CompareAndSwap(2, 4) && n.Load() == 3, "stale")
```

**Expected:** The first succeeds and the second fails.

A stale expectation detects changed state. A single-value CAS does not validate unrelated fields.

## 6. Transfer safe observation

Read an unchanged protected pair twice.

```go
p := &Pair{A: 4, B: 6}
a, b := p.Snapshot()
c, d := p.Snapshot()
check(a+b == 10 && c+d == 10, "snapshot")
```

**Expected:** Both snapshots preserve total 10.

An accessor hides locking without exposing mutable internals. Returning pointers to fields would bypass that boundary.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

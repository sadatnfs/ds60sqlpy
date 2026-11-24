# go-027: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A mutex protects a state invariant across several operations. Every relevant access must follow the same protocol: locking writes while reading without synchronization can still race. Atomic operations protect specific values and ordering relationships, but do not automatically make a multi-field transaction atomic. Prefer a mutex for a compound invariant that must be inspected and changed together. Never copy a mutex after use. Keep critical sections small, avoid calling unknown callbacks while holding a lock, and define lock ordering when several locks are unavoidable. A correct observed count is not by itself proof of correct synchronization.

sync.Mutex uses Lock and Unlock; defer Unlock after acquisition handles early returns. atomic.Int64 supplies typed Load, Store and Add. sync.Once runs one initialization function. Keep synchronized state in a pointer-owned holder so it is not copied accidentally. count++ on an ordinary shared integer is a read-modify-write sequence, not an atomic operation.

## 1. Protect a concurrent count: change one input

Copy worked example 1 into a scratch pad and change `for i := 0; i < 4; i++ {` to `for i := 1; i < 4; i++ {`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

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

**Expected:** The changed run panics with `count` because `c.Value() == 400` no longer holds. Restoring the original line brings back the worked observation: the joined final count is 400.

Reads and writes use the same lock. The join establishes task completion before inspection.

**Approach.** Count goroutines in the edited loop: starting at 1 and stopping before 4 launches three workers, each calling `Inc` 100 times.

**Why it holds here.** Every increment holds the mutex and `wg.Wait` joins all workers before `Value` reads, so the result is exactly 300 on every run and `c.Value() == 400` panics with `count`.

**A plausible wrong approach.** Predicting a different total on each run because goroutines interleave. The lock makes each increment indivisible and the join waits for all of them, so the value is deterministic; only an unlocked `c.n++` would lose updates.

**Verify.** Print `c.Value()` and see 300 before the panic. `go run -race` on the restored program reports no data race and prints the success line.

## 2. Use a typed atomic: debug a regression

A regression changed `n.Add(3)` to `n.Add(4)` in worked example 2. Run worked example 2 with that change, use the failure to explain the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
var n atomic.Int64
n.Add(3)
n.Add(4)
check(n.Load() == 7, "atomic")
```

**Expected:** Before the repair the program panics with `atomic`; after it the line reads `n.Add(3)` again and load returns 7.

Use the atomic access API consistently. Mixing it with ordinary conflicting accesses undermines the protocol.

**Approach.** Add the two deltas: with the regression both calls add 4, so `Load` returns 8 instead of 7.

**Why it holds here.** Atomic adds compose exactly, so 8 is the true sum of the regressed deltas and the check panics with `atomic`. Restoring the first delta to 3 gives 7.

**A plausible wrong approach.** Moving the adds into a helper `func add(c atomic.Int64, d int64)` that takes the counter by value. The helper increments a copy, so `n` misses that delta and the check still panics; `go vet` reports that the helper passes a lock by value because `atomic.Int64` contains a no-copy guard.

**Verify.** Print `n.Load()` and see 8 with the regression and 7 after the repair.

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

**Approach.** Move 3 from `A` to `B` inside one locked method, then read both fields with `Snapshot` under the same lock.

**Why it holds here.** Both fields change while the mutex is held, so no reader can see one update without the other: the snapshot is 2 and 8 and the sum stays 10.

**A plausible wrong approach.** Declaring `Transfer` with a value receiver. It locks and edits a copy of the `Pair`, the caller's fields stay 5 and 5 and the check panics with `pair`; `go vet` also reports that the method passes a lock by value.

**Verify.** Print `a, b` and see `2 8`, and run `go vet` to confirm no copylocks warning.

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

**Approach.** Call `once.Do` three times with the same `sync.Once`; only the first call runs the function.

**Why it holds here.** `Once` records that its function has run, so the second and third calls return immediately and `n` is 1.

**A plausible wrong approach.** Declaring `var once sync.Once` inside the loop. Each iteration gets a fresh `Once`, so the body runs three times, `n` is 3 and the check panics with `once`.

**Verify.** Print `n` and see 1; the in-loop declaration prints 3.

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

**Approach.** Store 2, swap it for 3 with `CompareAndSwap(2, 3)`, then try `CompareAndSwap(2, 4)` with the now stale expectation.

**Why it holds here.** The first swap finds 2 and succeeds. The second finds 3, which does not match 2, so it returns false and leaves the value at 3.

**A plausible wrong approach.** Retrying the stale swap in a loop, `for !n.CompareAndSwap(2, 4) {}`. The value is 3 and nothing changes it back, so the loop spins forever. A correct retry reloads the expected value each time, as in `old := n.Load()` then `CompareAndSwap(old, old+1)`.

**Verify.** Print the first result, the second result and `n.Load()` and see `true false 3`.

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

**Approach.** Read the same `Pair{A: 4, B: 6}` twice through `Snapshot`, which locks, copies both fields and unlocks.

**Why it holds here.** Nothing modifies the pair between the reads and each read is consistent, so both totals are 10.

**A plausible wrong approach.** Adding a locked `Total` method and calling it from inside `Snapshot` while `p.mu` is held. `sync.Mutex` is not reentrant, so the second `Lock` waits forever and the runtime reports that all goroutines are asleep.

**Verify.** Print `a, b, c, d` and see `4 6 4 6`. Run a concurrent `Transfer` between the snapshots under `go run -race` and both totals are still 10.

## Transfer after comparison

Start four goroutines that each call `Transfer(1)` 25 times on `Pair{A: 100, B: 0}`, join them and check the snapshot is 0 and 100. Add a locked `Swap` that exchanges the fields and check it gives 100 and 0. Explain which result a value receiver or a missing `wg.Wait` would produce.

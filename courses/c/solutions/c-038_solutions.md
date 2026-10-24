# c-038: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

Atomic types make individual accesses participate in a defined concurrency model. They are not interchangeable with volatile, and they do not automatically protect a multi-field invariant. The default sequentially consistent operations are a useful starting point. Weaker memory orders require a proof connecting the writer and reader. A release store can publish preceding writes to a reader whose acquire load observes that store. A relaxed counter can count independent events without publishing unrelated memory. Lock-free status is implementation-dependent; atomic does not mean every operation avoids a lock on every platform.

atomic_int declares an atomic integer and atomic_init initializes it before sharing. atomic_fetch_add returns the previous value. atomic_compare_exchange_strong updates only when the current value matches expected and writes the observed value back to expected on failure. memory_order_release and memory_order_acquire form a publication relationship when the acquire observes the release. Avoid hand-built lock-free containers until ownership, reclamation and ABA hazards are understood.

## Exercise 1: Inspect fetch-add semantics

Add 3 to an atomic integer initially 2.

```c
atomic_int value;
atomic_init(&value, 2);
int old = atomic_fetch_add(&value, 3);
CHECK(old == 2 && atomic_load(&value) == 5);
```

**Expected:** The returned old value is 2 and current value is 5.

The return value is the prior state. Confusing it with the new value can create off-by-one ticketing logic.

## Exercise 2: Compare and exchange successfully

Replace expected value 2 with 7.

```c
atomic_int value;
atomic_init(&value, 2);
int expected = 2;
CHECK(atomic_compare_exchange_strong(&value, &expected, 7));
CHECK(atomic_load(&value) == 7);
```

**Expected:** The operation succeeds and stores 7.

The update is conditional on the observed state, not an unconditional assignment.

## Exercise 3: Inspect failed compare-exchange

Attempt replacement with stale expected value 2 when current is 3.

```c
atomic_int value;
atomic_init(&value, 3);
int expected = 2;
CHECK(!atomic_compare_exchange_strong(&value, &expected, 7));
CHECK(expected == 3 && atomic_load(&value) == 3);
```

**Expected:** It fails and expected becomes 3.

The API returns current observation through expected, which a retry loop must handle deliberately.

## Exercise 4: Count independent events

Perform ten relaxed increments before reading in the same thread.

```c
atomic_int count;
atomic_init(&count, 0);
for (int i = 0; i < 10; i++)
  atomic_fetch_add_explicit(&count, 1, memory_order_relaxed);
CHECK(atomic_load_explicit(&count, memory_order_relaxed) == 10);
```

**Expected:** The count is 10.

This fixture demonstrates the counter API, not publication of unrelated memory. A concurrent relaxed counter has a different reasoning purpose from a readiness flag.

## Exercise 5: Publish initialized data

Use a release flag from a worker and acquire it before reading its payload.

```c
struct Publication p;
atomic_init(&p.ready, false);
p.value = 0;
pthread_t worker;
CHECK(pthread_create(&worker, NULL, atomic_publisher, &p) == 0);
while (!atomic_load_explicit(&p.ready, memory_order_acquire)) {
  sched_yield();
}
CHECK(p.value == 42);
CHECK(pthread_join(worker, NULL) == 0);
```

**Expected:** The payload is 42.

The payload read follows the acquire observation of the release store. Changing the flag to an ordinary or merely volatile object would remove the required synchronization.

## Exercise 6: Transfer an atomic exchange

Replace a flag value and inspect the returned prior state.

```c
atomic_bool ready;
atomic_init(&ready, false);
bool old = atomic_exchange(&ready, true);
CHECK(!old && atomic_load(&ready));
```

**Expected:** The old state is false and the new state true.

Exchange is one atomic operation. A separate load then store would not provide the same indivisible state transition under concurrent access.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.

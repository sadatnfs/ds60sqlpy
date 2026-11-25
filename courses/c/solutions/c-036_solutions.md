# c-036: explained solutions

`c-036_solution.c` assembles the "join one calculation" case through the "transfer reusable execution" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A thread executes concurrently within the process and shares its address space. Passing a pointer to a thread does not extend the target lifetime. Keep the argument object alive until the worker no longer accesses it, normally by joining the worker before leaving its owning scope. Each worker can write to distinct result storage without a mutex when no conflicting access occurs and the parent waits before reading. Shared mutation needs synchronization, taught next. Thread creation and joining can fail, so their return values belong to the resource contract. Detached threads require a different ownership design and are not a shortcut around joining.

pthread_create takes a pointer to a pthread_t, optional attributes, a function void *(*)(void *) and an argument pointer. The worker converts that argument back to its actual type. pthread_join waits for termination and can retrieve a returned pointer, whose lifetime still needs justification. POSIX pthread functions generally return an error number directly rather than setting errno in the same way as read or write.

## Exercise 1: Join one calculation: change one input

In worked example 1, change `struct Work work = {.input = 7, .output = 0};` to `struct Work work = {.input = 8, .output = 0};`. Predict which value the CHECK on `work.output == 49` sees, then run and restore.

The unchanged code is worked example 1:

```c
struct Work work = {.input = 7, .output = 0};
pthread_t thread;
CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
CHECK(pthread_join(thread, NULL) == 0);
CHECK(work.output == 49);
```

**Expected:** `Check failed` at `work.output == 49`; restoring `struct Work work = {.input = 7, .output = 0};` passes again.

**Verify:** Name the value that made `work.output == 49` false, where worked example 1 showed that the retained result is 49.

The stack argument remains alive until after join. Reading output before synchronization would not have this contract.

## Exercise 2: Keep separate arguments: debug a regression

Worked example 2 now has a line reading `struct Work work[2] = {{3, 0}, {3, 0}};`. Repair it so that their independent outputs are 4 and 9 again.

The unchanged code is worked example 2:

```c
struct Work work[2] = {{2, 0}, {3, 0}};
pthread_t threads[2];
for (size_t i = 0; i < 2; i++)
  CHECK(pthread_create(&threads[i], NULL, square_worker, &work[i]) == 0);
for (size_t i = 0; i < 2; i++)
  CHECK(pthread_join(threads[i], NULL) == 0);
CHECK(work[0].output == 4 && work[1].output == 9);
```

**Expected:** `Check failed` at `work[0].output == 4 && work[1].output == 9` until the line reads `struct Work work[2] = {{2, 0}, {3, 0}};` again.

**Verify:** Explain how `struct Work work[2] = {{3, 0}, {3, 0}};` changes the value `work[0].output == 4 && work[1].output == 9` tests, using your failing and repaired runs.

Each worker receives its own stable object rather than the address of one changing loop variable.

## Exercise 3: Retrieve a stable pointer result

Have the worker return its caller-owned argument pointer.

```c
struct Work work = {5, 0};
pthread_t thread;
void *returned = NULL;
CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
CHECK(pthread_join(thread, &returned) == 0);
CHECK(returned == &work && work.output == 25);
```

**Expected:** Join returns that same live object address.

**Verify:** Keep a CHECK equivalent to `returned == &work && work.output == 25`. Control edit: changing `struct Work work = {5, 0};` to `struct Work work = {6, 0};` must fail it; then restore it.

The returned pointer is valid because the caller still owns its storage. Returning a pointer to a worker-local automatic object would be invalid.

## Exercise 4: Handle a zero input

Run the worker on input zero.

```c
struct Work work = {0, 9};
pthread_t thread;
CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
CHECK(pthread_join(thread, NULL) == 0);
CHECK(work.output == 0);
```

**Expected:** The output is zero.

**Verify:** Keep a CHECK equivalent to `work.output == 0`. Control edit: changing `struct Work work = {0, 9};` to `struct Work work = {1, 9};` must fail it; then restore it.

The result demonstrates real computation rather than relying on the initial output field.

## Exercise 5: Aggregate after all joins

Run four workers for inputs 1 through 4 and sum results afterward.

```c
struct Work work[4] = {{1, 0}, {2, 0}, {3, 0}, {4, 0}};
pthread_t threads[4];
for (size_t i = 0; i < 4; i++)
  CHECK(pthread_create(&threads[i], NULL, square_worker, &work[i]) == 0);
int sum = 0;
for (size_t i = 0; i < 4; i++) {
  CHECK(pthread_join(threads[i], NULL) == 0);
  sum += work[i].output;
}
CHECK(sum == 30);
```

**Expected:** The total is 30.

**Verify:** Keep a CHECK equivalent to `sum == 30`. Control edit: changing `sum += work[i].output;` to `sum -= work[i].output;` must fail it; then restore it.

Only the parent mutates the aggregate. Worker completion order does not change the integer result.

## Exercise 6: Transfer reusable execution

Run the same argument object through two joined invocations sequentially.

```c
struct Work work = {3, 0};
pthread_t thread;
CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
CHECK(pthread_join(thread, NULL) == 0);
work.input = 4;
CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
CHECK(pthread_join(thread, NULL) == 0);
CHECK(work.output == 16);
```

**Expected:** The second input produces its own output 16.

**Verify:** Keep a CHECK equivalent to `work.output == 16`. Control edit: changing `work.input = 4;` to `work.input = 5;` must fail it; then restore it.

Reusing storage is safe after the previous worker has finished. Overlapping invocations on the same mutable argument would need synchronization.

## After comparison

Start two threads, each with its own `struct Work` holding 5 and 6, join both and CHECK the outputs 25 and 36. Then explain as text why a loop that reuses one `struct Work` for both `pthread_create` calls races: the second iteration can overwrite `input` before the first worker reads it. Give each thread its own object, as Exercise 2 does, or join before reusing one.

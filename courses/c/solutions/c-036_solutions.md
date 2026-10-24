# c-036: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A thread executes concurrently within the process and shares its address space. Passing a pointer to a thread does not extend the target lifetime. Keep the argument object alive until the worker no longer accesses it, normally by joining the worker before leaving its owning scope. Each worker can write to distinct result storage without a mutex when no conflicting access occurs and the parent waits before reading. Shared mutation needs synchronization, taught next. Thread creation and joining can fail, so their return values belong to the resource contract. Detached threads require a different ownership design and are not a shortcut around joining.

pthread_create takes a pointer to a pthread_t, optional attributes, a function void *(*)(void *) and an argument pointer. The worker converts that argument back to its actual type. pthread_join waits for termination and can retrieve a returned pointer, whose lifetime still needs justification. POSIX pthread functions generally return an error number directly rather than setting errno in the same way as read or write.

## Exercise 1: Join one calculation

Start a thread squaring input 7 and join it.

```c
struct Work work = {.input = 7, .output = 0};
pthread_t thread;
CHECK(pthread_create(&thread, NULL, square_worker, &work) == 0);
CHECK(pthread_join(thread, NULL) == 0);
CHECK(work.output == 49);
```

**Expected:** The retained result is 49.

The stack argument remains alive until after join. Reading output before synchronization would not have this contract.

## Exercise 2: Keep separate arguments

Start two workers with inputs 2 and 3.

```c
struct Work work[2] = {{2, 0}, {3, 0}};
pthread_t threads[2];
for (size_t i = 0; i < 2; i++)
  CHECK(pthread_create(&threads[i], NULL, square_worker, &work[i]) == 0);
for (size_t i = 0; i < 2; i++)
  CHECK(pthread_join(threads[i], NULL) == 0);
CHECK(work[0].output == 4 && work[1].output == 9);
```

**Expected:** Their independent outputs are 4 and 9.

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

Reusing storage is safe after the previous worker has finished. Overlapping invocations on the same mutable argument would need synchronization.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.

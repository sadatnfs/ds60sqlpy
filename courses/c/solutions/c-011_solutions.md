# c-011: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-011_solution.c`, implements all six cases, from the "trace block shadowing" case to the "transfer initialized aggregation" case, in one `main.c`.

## Mechanism and assumptions

Scope determines where a name is visible; lifetime determines when its object exists. They are related but different. An automatic local object usually lasts until its block ends. A static-storage object exists for the program duration even when its name is visible only inside one function. Allocated storage has a lifetime controlled by allocation and release, taught next. A pointer does not extend any of these lifetimes automatically. Returning an automatic local address is invalid after return, while returning a static object address can be valid but introduces shared mutable state and reentrancy concerns.

A block can shadow an outer variable with the same name. static inside a function preserves one object across calls and zero-initializes it before execution. A file-scope static declaration also restricts linkage to the translation unit. These are different uses of the same keyword. Keep automatic variables explicitly initialized before reading them. Do not use the value of a pointer after its target lifetime has ended.

## Exercise 1: Trace block shadowing: change one input

Copy worked example 1, the "trace block shadowing" case, into a scratch pad and change `int value = 3;` to `int value = 4;`. Before running, predict which CHECK fails and which value it sees in place of the worked result (after the inner block, the outer remains 3); then run it and restore the original line.

The unchanged code is worked example 1:

```c
int value = 3;
{
  int value = 7;
  CHECK(value == 7);
}
CHECK(value == 3);
```

**Expected:** With `int value = 4;` the run stops with `Check failed` at the CHECK on `value == 3`, because the "trace block shadowing" case no longer shows that after the inner block, the outer remains 3. Restoring `int value = 3;` brings that observation back.

The names are the same but designate distinct objects. Shadowing can be legal while still reducing readability.

**Approach.** Trace both objects: the outer `value` now starts at 4, the inner block declares a new `value` set to 7, and after the block the name refers to the outer object again.

**Why it holds here.** The inner CHECK reads the inner object and passes with 7. The outer object was never touched, so it still holds 4 and the CHECK on 3 fails.

**A plausible wrong approach.** Predicting the inner CHECK fails because the inner `value` starts from the outer 4. The inner declaration creates a separate object with its own initializer, 7, so only the outer CHECK sees the edit.

**Verify.** Print `value` inside the block and after it, and see 7 and then 4.

## Exercise 2: Retain static state: diagnose an edited check

A careless edit changed the CHECK in worked example 2, the "retain static state" case, so that it reads `CHECK(next_count() != 2);`. Run the example with that line, explain why the edited CHECK now fails even though the program state still means it returns 1 and then 2, and restore it.

The unchanged code is worked example 2:

```c
CHECK(next_count() == 1);
CHECK(next_count() == 2);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `next_count() == 2`. Once the line reads `CHECK(next_count() == 2);` again, the "retain static state" case again shows that it returns 1 and then 2.

The counter is initialized once and survives function returns. This shared state would require synchronization if called concurrently.

**Approach.** Count the calls: the first CHECK consumes the first call, which returns 1, and the edited CHECK makes the second call, which returns 2.

**Why it holds here.** `count` has static storage duration: it is initialized once and keeps its value between calls, so the second call returns 2 and `2 != 2` is false.

**A plausible wrong approach.** Predicting the edited CHECK passes because `count` is reset to 0 on every call, so the second call would return 1. The initializer of a static local runs once, before the first call, not on each entry.

**Verify.** Call `next_count()` three times in separate statements and print each result: 1, 2, 3.

## Exercise 3: Return a static address

Get a pointer to a static read-only value.

```c
const int *p = static_value();
CHECK(*p == 7);
```

**Expected:** The target remains valid and equals 7.

The target lifetime spans the program. const restricts mutation through this pointer but does not make every static design automatically thread-safe.

**Approach.** Return the address of a `static const` object and read it through the returned pointer.

**Why it holds here.** A static object lives for the entire program, so the pointer stays valid after `static_value` returns and `*p` is 7.

**A plausible wrong approach.** Returning the address of an ordinary local, `int value = 7; return &value;`. The object ends when the function returns, so any later read is undefined; Clang reports `address of stack memory associated with local variable returned` and GCC reports `-Wreturn-local-addr`.

**Verify.** Compile a helper with the local version and read the warning without calling it; run the static version and see 7.

## Exercise 4: Keep automatic state per call

Call a function with an initialized local counter twice.

```c
CHECK(local_count() == 1 && local_count() == 1);
```

**Expected:** Both calls return 1.

Each call creates a fresh automatic object. This differs from the retained static counter.

**Approach.** Call `local_count` twice: each call creates a fresh `count` initialized to 0, increments it and returns 1.

**Why it holds here.** Automatic objects are created on every entry and destroyed on return, so the second call cannot see the first call's 1, and both operands of `&&` are true.

**A plausible wrong approach.** Adding `static` to the local, `static int count = 0;`. That turns the function into `next_count`: the second call returns 2, so `local_count() == 1` fails on the right side of `&&`.

**Verify.** Call `local_count()` twice in separate statements and see 1 and 1, while `next_count()` keeps counting upward.

## Exercise 5: Separate visibility from lifetime

Retain a value copy obtained from an inner block.

```c
int copy = 0;
{
  int local = 9;
  copy = local;
}
CHECK(copy == 9);
```

**Expected:** The copied scalar remains 9 afterward.

The scalar copy has its own lifetime. Retaining &local instead would produce an invalid pointer after the block.

**Approach.** Copy the inner block's value into `copy`, declared in the outer scope, before the block ends.

**Why it holds here.** The assignment copies the integer 9 into `copy`, which lives until the end of `main`, so ending `local`'s lifetime does not affect it.

**A plausible wrong approach.** Keeping the address instead, `int *keep; { int local = 9; keep = &local; } CHECK(*keep == 9);`. After the block `local` no longer exists, so the read is undefined even if it happens to print 9; AddressSanitizer reports it as stack use after scope. Describe it rather than run it.

**Verify.** Print `copy` after the block and see 9.

## Exercise 6: Transfer initialized aggregation

Initialize an accumulator before processing an empty range.

```c
int total = 0;
size_t count = 0;
for (size_t i = 0; i < count; i++)
  total += (int)i;
CHECK(total == 0);
```

**Expected:** The result is the defined zero identity.

Reading an uninitialized automatic accumulator would not be repaired by an empty loop. Initialization is part of the algorithm.

**Approach.** Initialize `total` to 0 before the loop, so an empty range leaves the identity value.

**Why it holds here.** With `count` 0 the condition `i < count` is false at once, the body never runs, and `total` keeps the 0 it was given.

**A plausible wrong approach.** Declaring `int total;` without an initializer and relying on the loop to set it. With an empty range the loop never assigns it, so the CHECK reads an indeterminate value, which is undefined. Clang warns that `total` is uninitialized when used, and GCC may not warn without optimization.

**Verify.** Compile the uninitialized version with `-Wall` to see the warning without running it; run the initialized version and see the success line.

## After comparison

Write `int next_id(void)` and `void reset_ids(void)` that share a file-scope `static int next = 100;`. Check that two calls give 100 and 101, a reset followed by a call gives 100 again, and `local_count` still returns 1 throughout. Explain why moving the counter into `next_id` as an automatic local returns 100 every time, and why a `static` local inside `next_id` would leave `reset_ids` unable to reach it.

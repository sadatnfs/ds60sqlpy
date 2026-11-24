# c-020: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-020_solution.c`, implements all six cases, from the "invoke through a function pointer" case to the "transfer an empty callback traversal" case, in one `main.c`.

## Mechanism and assumptions

A function pointer lets a component accept behavior as data. The function type must match the call interface; casting an incompatible function pointer does not make the call valid. A callback contract also describes when it is invoked, whether it may retain input pointers and how errors are reported. qsort accepts a comparator returning negative, zero or positive according to ordering. Subtracting integers to implement comparison can overflow, so compare relationally instead. Sorting correctness depends on a consistent comparator; a contradictory ordering can invalidate algorithm assumptions even when individual calls compile.

int (*compare)(const void *,const void *) declares a function pointer rather than a function returning a pointer. qsort passes pointers to elements, which the comparator converts to the correct element type. (a>b)-(a<b) yields the required sign without subtracting the values themselves. A separate callback context can carry state when an API provides one; avoid hidden global mutable state for reusable components.

## Exercise 1: Invoke through a function pointer: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(transform(4) == 8);` to `CHECK(transform(5) == 8);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
int (*transform)(int) = double_value;
CHECK(transform(4) == 8);
```

**Expected:** With `CHECK(transform(5) == 8);` the run stops with `Check failed` at the CHECK on `transform(4) == 8`, because the "invoke through a function pointer" case no longer shows that the result is 8. Restoring `CHECK(transform(4) == 8);` brings that observation back.

The pointer type agrees with the function declaration, so the compiler can check the call.

**Approach.** Follow the call through the pointer: `transform(5)` calls `double_value(5)`, which returns 10.

**Why it holds here.** A function pointer stores which function to call, not a result, so each call evaluates its argument afresh; 10 is not 8 and the CHECK fails.

**A plausible wrong approach.** Declaring the pointer with a different parameter type, such as `int (*transform)(long) = double_value;`, to make it accept more inputs. Clang rejects it with `incompatible function pointer types`, and forcing it with a cast would make every call undefined.

**Verify.** Print `transform(4)` and `transform(5)` and see 8 and 10.

## Exercise 2: Sort integers safely: debug a regression

A regression changed one token in worked example 2, the "sort integers safely" case, so one line now reads `int values[] = {4, 1, 2};`. Run the example with that line, use the failing CHECK to find why the order becomes 1, 2, 3 no longer holds and repair the line without changing the CHECK.

The unchanged code is worked example 2:

```c
int values[] = {3, 1, 2};
qsort(values, 3, sizeof values[0], compare_ints);
CHECK(values[0] == 1 && values[1] == 2 && values[2] == 3);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `values[0] == 1 && values[1] == 2 && values[2] == 3`. Once the line reads `int values[] = {3, 1, 2};` again, the "sort integers safely" case again shows that the order becomes 1, 2, 3.

The comparator reports ordering rather than a numeric distance between elements.

**Approach.** Run the sort and read the result: `{4, 1, 2}` becomes `1, 2, 4`, so the first two operands pass and `values[2] == 3` fails.

**Why it holds here.** `compare_ints` orders the elements correctly; the regression is in the data, and restoring `{3, 1, 2}` gives 1, 2, 3.

**A plausible wrong approach.** Suspecting the `qsort` call and rewriting it as `qsort(values, sizeof values, sizeof values[0], compare_ints)`. That passes 12 as the element count for a 3-element array, so `qsort` reads and writes past the end, which is undefined; the count is `sizeof values / sizeof values[0]`.

**Verify.** Print the three elements after sorting and see `1 2 4` before the repair and `1 2 3` after it.

## Exercise 3: Compare extreme values

Compare INT_MIN and INT_MAX.

```c
int a = INT_MIN, b = INT_MAX;
CHECK(compare_ints(&a, &b) < 0);
```

**Expected:** The result correctly reports the first is smaller.

Returning a-b would overflow for this case. Relational comparisons avoid that undefined behavior.

**Approach.** Return `(a > b) - (a < b)`, which yields -1, 0 or 1 from two comparisons that cannot overflow.

**Why it holds here.** For `INT_MIN` and `INT_MAX`, `a > b` is 0 and `a < b` is 1, so the result is -1, and `< 0` holds.

**A plausible wrong approach.** Returning `a - b`. The true difference is -4294967295, which does not fit in `int`, so the subtraction is signed overflow and undefined; on two's complement hardware it typically wraps to 1 and reports `INT_MIN` as the larger value. UBSan reports it as a signed integer overflow.

**Verify.** Compute the difference in `long long` and see -4294967295, and print `compare_ints(&a, &b)` and see -1.

## Exercise 4: Retain equal values

Sort duplicate values 2, 1, 2.

```c
int values[] = {2, 1, 2};
qsort(values, 3, sizeof values[0], compare_ints);
CHECK(values[0] == 1 && values[1] == 2 && values[2] == 2);
```

**Expected:** Both copies of 2 remain.

Sorting reorders elements; it does not deduplicate them. qsort also does not promise stable order among equal keys.

**Approach.** Return 0 for equal keys, so both 2s compare equal and stay in the array.

**Why it holds here.** `qsort` permutes elements and never removes them, and a comparator that returns 0 for equal keys is consistent, so the result is 1, 2, 2.

**A plausible wrong approach.** Writing a comparator that never returns 0, such as `return a < b ? -1 : 1;`. It reports each 2 as greater than the other, which violates the consistency `qsort` requires, so the behavior is undefined even if one run looks sorted. Describe it rather than rely on it.

**Verify.** Print the sorted array and see `1 2 2`, and check that `compare_ints` on two equal `int`s returns 0.

## Exercise 5: Inject a predicate

Count even values in 1, 2, 3, 4 through a callback.

```c
int values[] = {1, 2, 3, 4};
CHECK(count_if(values, 4, is_even) == 2);
```

**Expected:** The count is 2.

Traversal and selection policy are separate responsibilities with a clear typed interface.

**Approach.** Pass the function name `is_even` as the predicate; `count_if` calls it once per element.

**Why it holds here.** 2 and 4 satisfy `value % 2 == 0` and 1 and 3 do not, so the count is 2.

**A plausible wrong approach.** Writing the opposite predicate as `value % 2 == 1` and reusing it on negative data. In C, `-3 % 2` is -1, so that predicate misses every negative odd number; `value % 2 != 0` is the correct test.

**Verify.** Print `-3 % 2` and see -1, then print `count_if(values, 4, is_even)` and see 2.

## Exercise 6: Transfer an empty callback traversal

Count over zero logical elements.

```c
CHECK(count_if(NULL, 0, is_even) == 0);
```

**Expected:** The result is zero and no element is accessed.

This helper explicitly accepts the empty null view because it makes no callback or element access.

**Approach.** Let the loop condition `i < n` guard every element read and every callback.

**Why it holds here.** With `n` 0 the condition is false at once, so neither `values[i]` nor `predicate` is evaluated, and passing `NULL` is safe.

**A plausible wrong approach.** Rewriting the loop as `do { ... } while (++i < n);`. The body runs once before the test, so it reads `values[0]` through the null pointer, which is undefined and usually crashes.

**Verify.** Run the original and see the success line; put a counter in a test predicate and confirm it was called 0 times.

## After comparison

Write `size_t count_if_ctx(const int *values, size_t n, bool (*pred)(int, void *), void *ctx)` and a predicate `bool above(int value, void *ctx)` that compares with `*(const int *)ctx`. Check that `{1, 5, 9}` with threshold 4 gives 2, threshold 9 gives 0 and `n` 0 with `NULL` gives 0. Explain why the context pointer replaces a global threshold, and what goes wrong if `ctx` points at a local that has gone out of scope.

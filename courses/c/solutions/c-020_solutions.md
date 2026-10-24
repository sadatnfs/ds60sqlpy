# c-020: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A function pointer lets a component accept behavior as data. The function type must match the call interface; casting an incompatible function pointer does not make the call valid. A callback contract also describes when it is invoked, whether it may retain input pointers and how errors are reported. qsort accepts a comparator returning negative, zero or positive according to ordering. Subtracting integers to implement comparison can overflow, so compare relationally instead. Sorting correctness depends on a consistent comparator; a contradictory ordering can invalidate algorithm assumptions even when individual calls compile.

int (*compare)(const void *,const void *) declares a function pointer rather than a function returning a pointer. qsort passes pointers to elements, which the comparator converts to the correct element type. (a>b)-(a<b) yields the required sign without subtracting the values themselves. A separate callback context can carry state when an API provides one; avoid hidden global mutable state for reusable components.

## Exercise 1: Invoke through a function pointer

Assign a doubling function and call it with 4.

```c
int (*transform)(int) = double_value;
CHECK(transform(4) == 8);
```

**Expected:** The result is 8.

The pointer type agrees with the function declaration, so the compiler can check the call.

## Exercise 2: Sort integers safely

Sort 3, 1, 2 with a relational comparator.

```c
int values[] = {3, 1, 2};
qsort(values, 3, sizeof values[0], compare_ints);
CHECK(values[0] == 1 && values[1] == 2 && values[2] == 3);
```

**Expected:** The order becomes 1, 2, 3.

The comparator reports ordering rather than a numeric distance between elements.

## Exercise 3: Compare extreme values

Compare INT_MIN and INT_MAX.

```c
int a = INT_MIN, b = INT_MAX;
CHECK(compare_ints(&a, &b) < 0);
```

**Expected:** The result correctly reports the first is smaller.

Returning a-b would overflow for this case. Relational comparisons avoid that undefined behavior.

## Exercise 4: Retain equal values

Sort duplicate values 2, 1, 2.

```c
int values[] = {2, 1, 2};
qsort(values, 3, sizeof values[0], compare_ints);
CHECK(values[0] == 1 && values[1] == 2 && values[2] == 2);
```

**Expected:** Both copies of 2 remain.

Sorting reorders elements; it does not deduplicate them. qsort also does not promise stable order among equal keys.

## Exercise 5: Inject a predicate

Count even values in 1, 2, 3, 4 through a callback.

```c
int values[] = {1, 2, 3, 4};
CHECK(count_if(values, 4, is_even) == 2);
```

**Expected:** The count is 2.

Traversal and selection policy are separate responsibilities with a clear typed interface.

## Exercise 6: Transfer an empty callback traversal

Count over zero logical elements.

```c
CHECK(count_if(NULL, 0, is_even) == 0);
```

**Expected:** The result is zero and no element is accessed.

This helper explicitly accepts the empty null view because it makes no callback or element access.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.

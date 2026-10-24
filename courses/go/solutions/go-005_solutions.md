# go-005: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

An array includes its length in its type and owns a fixed sequence of elements. A slice is a descriptor containing a pointer into backing storage, a length and a capacity. Copying that descriptor does not copy the elements. Two slices can therefore observe each other's mutations. append may reuse available storage or allocate new storage; code must not depend on which choice happens unless it controls the capacity contract. A full slice expression can restrict capacity and force a later append to allocate. The practical question is not whether a value looks like a collection, but who can mutate the same storage and for how long.

[]int constructs a slice type; [3]int constructs an array type. values[a:b] selects indices a through b-1. len is the visible element count and cap is the maximum length before reallocation is required. copy(dst,src) copies the smaller length and returns that count. append returns a new slice descriptor, so retain the returned value. A nil slice has length zero and can be appended to.

## 1. Observe shared storage

Take the first two elements of 1, 2, 3 and change the first through the slice.

```go
values := []int{1, 2, 3}
view := values[:2]
view[0] = 9
check(values[0] == 9, "alias")
```

**Expected:** The original first element becomes 9.

Slicing constructs a view over existing storage. It does not give the new variable independent ownership of its elements.

## 2. Make an independent copy

Copy 1, 2, 3 into a new slice and mutate that copy.

```go
values := []int{1, 2, 3}
cloned := append([]int(nil), values...)
cloned[0] = 9
check(values[0] == 1 && cloned[0] == 9, "copy")
```

**Expected:** The original stays 1 while the copy starts 9.

Appending into initially nil storage allocates enough backing storage for these nonempty values. Nested pointers would still require a deeper copy policy.

## 3. Restrict append capacity

Take values[:1:1] and append 8.

```go
values := []int{1, 2, 3}
limited := values[:1:1]
grown := append(limited, 8)
check(values[1] == 2 && grown[1] == 8, "capacity boundary")
```

**Expected:** The original second element remains 2.

The three-index form caps available capacity at one. append must allocate to grow, which separates subsequent writes to the grown slice.

## 4. Inspect a truncated copy

Copy three source elements into a length-two destination.

```go
dst := make([]int, 2)
n := copy(dst, []int{4, 5, 6})
check(n == 2 && dst[1] == 5, "copy length")
```

**Expected:** Exactly two elements are copied.

Capacity alone does not determine how many elements copy writes; the destination length is the bound.

## 5. Grow an empty slice

Append 7 to a nil slice.

```go
var values []int
check(values == nil && len(values) == 0, "nil slice")
values = append(values, 7)
check(len(values) == 1 && values[0] == 7, "append nil")
```

**Expected:** The result has length 1 and value 7.

Nil is an empty slice value with no backing array. It supports ordinary append without an explicit allocation call.

## 6. Transfer array semantics

Copy a fixed array and mutate the copy.

```go
a := [2]int{1, 2}
b := a
b[0] = 9
check(a[0] == 1 && b[0] == 9, "array copy")
```

**Expected:** The original array remains unchanged.

Array assignment copies every element, unlike slice-descriptor assignment. This contrast explains why representation affects mutation behavior.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

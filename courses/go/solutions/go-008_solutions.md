# go-008: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-008_solution.go` implements all six cases.

## Mechanism

A struct groups named fields into one value. Naming fields makes the domain visible: a coordinate with X and Y is more readable than an unexplained two-element slice. Struct assignment copies fields, but fields containing slices, maps or pointers can continue to share referenced storage. Exported fields begin with uppercase letters, which also affects reflection-based encoders. Zero values are predictable, yet not every zero struct is a valid domain object. A constructor-like function can validate inputs and return a value plus error, but Go does not require all construction to pass through such a function. Choose visibility and validation together.

type Point struct { X, Y int } creates a named type with fields. Point{X:2,Y:3} uses keyed construction, so field meaning survives reordering. p.X selects a field. Comparable structs can be compared with == only if every field is comparable. A struct with a slice cannot be a map key. An anonymous embedded field promotes selectors but does not create class inheritance.

## 1. Model a coordinate: change one input

Copy worked example 1, change `p := Point{X: 2, Y: 3}` to `p := Point{X: 3, Y: 3}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
p := Point{X: 2, Y: 3}
check(p.X+p.Y == 5, "point")
```

**Expected:** The edited run panics with `point` because `p.X+p.Y == 5` no longer holds.

**Verify:** Restoring `p := Point{X: 2, Y: 3}` makes the check pass again with the worked observation: the distance is 5.

Named fields document the coordinate meaning. This tiny case assumes nonnegative coordinates; a general distance function needs absolute values.

## 2. Observe scalar copy: debug a regression

A one-token regression in worked example 2 makes a line read `a := Point{X: 3, Y: 3}`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
a := Point{X: 2, Y: 3}
b := a
b.X = 9
check(a.X == 2 && b.X == 9, "struct copy")
```

**Expected:** The defective run panics with `struct copy`; after restoring `a := Point{X: 2, Y: 3}`, the original X remains 2.

**Verify:** The failing run shows message `struct copy`; after the repair `a.X == 2 && b.X == 9` holds again.

Both fields contain scalar values, so assignment produces independent field storage.

## 3. Expose a shallow field

Copy a Batch struct containing a slice and mutate its first item.

```go
a := Batch{Items: []int{1, 2}}
b := a
b.Items[0] = 9
check(a.Items[0] == 9, "shallow field")
```

**Expected:** The original batch observes the mutation.

**Verify:** Your solution must keep `a.Items[0] == 9` true. Control: changing `b.Items[0] = 9` to `b.Items[1] = 9` panics with message `shallow field`; revert it.

The copied slice descriptor still points to the same backing array. A struct wrapper does not change the ownership semantics of its fields.

## 4. Inspect zero state

Declare a Point without a literal.

```go
var p Point
check(p == (Point{X: 0, Y: 0}), "struct zero")
```

**Expected:** Both coordinates are 0.

**Verify:** Your solution must keep `p == (Point{X: 0, Y: 0})` true. Control: changing `check(p == (Point{X: 0, Y: 0}), "struct zero")` to `check(p == (Point{X: 1, Y: 0}), "struct zero")` panics with message `struct zero`; revert it.

Field zero values compose into a deterministic struct zero value. Whether that represents a meaningful domain object is a separate contract.

## 5. Use a comparable key

Store a label keyed by Point and retrieve it with an equal Point.

```go
m := map[Point]string{{X: 0, Y: 0}: "origin"}
check(m[Point{}] == "origin", "struct key")
```

**Expected:** The equal coordinate finds origin.

**Verify:** Your solution must keep `m[Point{}] == "origin"` true. Control: changing `m := map[Point]string{{X: 0, Y: 0}: "origin"}` to `m := map[Point]string{{X: 1, Y: 0}: "origin"}` panics with message `struct key`; revert it.

Equality compares corresponding fields. Replacing a field with a slice would make this struct noncomparable and the map key invalid at compilation.

## 6. Transfer validation

Construct a named item with an empty name and then a valid name.

```go
_, err := newItem("")
check(err != nil, "blank name")
item, err := newItem("sample")
check(err == nil && item.Name == "sample", "valid item")
```

**Expected:** The empty name is rejected; the valid name is retained.

**Verify:** Your solution must keep `err == nil && item.Name == "sample"` true. Control: changing `item, err := newItem("sample")` to `item, err := newItem("sample!")` panics with message `valid item`; revert it.

Validation at construction reduces invalid states, but exported fields still allow later assignment. A stricter API would keep invariant-bearing fields unexported.

## Transfer after comparison

A struct makes the domain visible, but ownership and validity remain separate decisions. Copying is shallow, a zero value may or may not be meaningful, and exported fields allow later invalid assignments. When later lessons decode JSON into structs or model Kubernetes objects, ask which fields share storage after a copy, which zero values are valid and which invariants must be enforced at construction.

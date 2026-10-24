# go-008: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A struct groups named fields into one value. Naming fields makes the domain visible: a coordinate with X and Y is more readable than an unexplained two-element slice. Struct assignment copies fields, but fields containing slices, maps or pointers can continue to share referenced storage. Exported fields begin with uppercase letters, which also affects reflection-based encoders. Zero values are predictable, yet not every zero struct is a valid domain object. A constructor-like function can validate inputs and return a value plus error, but Go does not require all construction to pass through such a function. Choose visibility and validation together.

type Point struct { X, Y int } creates a named type with fields. Point{X:2,Y:3} uses keyed construction, so field meaning survives reordering. p.X selects a field. Comparable structs can be compared with == only if every field is comparable. A struct with a slice cannot be a map key. An anonymous embedded field promotes selectors but does not create class inheritance.

## 1. Model a coordinate

Construct Point with X 2 and Y 3 and calculate Manhattan distance from the origin.

```go
p := Point{X: 2, Y: 3}
check(p.X+p.Y == 5, "point")
```

**Expected:** The distance is 5.

Named fields document the coordinate meaning. This tiny case assumes nonnegative coordinates; a general distance function needs absolute values.

## 2. Observe scalar copy

Copy a Point and change the copied X field.

```go
a := Point{X: 2, Y: 3}
b := a
b.X = 9
check(a.X == 2 && b.X == 9, "struct copy")
```

**Expected:** The original X remains 2.

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

The copied slice descriptor still points to the same backing array. A struct wrapper does not change the ownership semantics of its fields.

## 4. Inspect zero state

Declare a Point without a literal.

```go
var p Point
check(p == (Point{X: 0, Y: 0}), "struct zero")
```

**Expected:** Both coordinates are 0.

Field zero values compose into a deterministic struct zero value. Whether that represents a meaningful domain object is a separate contract.

## 5. Use a comparable key

Store a label keyed by Point and retrieve it with an equal Point.

```go
m := map[Point]string{{X: 0, Y: 0}: "origin"}
check(m[Point{}] == "origin", "struct key")
```

**Expected:** The equal coordinate finds origin.

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

Validation at construction reduces invalid states, but exported fields still allow later assignment. A stricter API would keep invariant-bearing fields unexported.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

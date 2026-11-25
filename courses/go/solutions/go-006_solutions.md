# go-006: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-006_solution.go` implements all six cases.

## Mechanism

A map associates keys with values. Reading an absent key returns the value type's zero value, which can be indistinguishable from a present key whose value is zero. The comma-ok form retains the presence information. Map iteration order is deliberately unspecified; reproducible reports must extract and sort keys rather than rely on an observed order. Maps share mutable storage when assigned, and ordinary maps are not safe for concurrent mutation without synchronization. A nil map can be read but cannot accept an assignment. Treat these properties as part of the data model when building counters, caches and configuration overlays.

map[string]int declares string keys and integer values. value, ok := counts[key] distinguishes absence from zero. make initializes writable map storage. delete removes a key and is harmless if the key is absent. range gives key/value pairs in an unspecified order. Use sort.Strings on extracted keys before producing ordered output.

## 1. Distinguish zero from missing: change one input

Copy worked example 1, change `m := map[string]int{"zero": 0}` to `m := map[string]int{"zero": 1}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
m := map[string]int{"zero": 0}
a, okA := m["zero"]
b, okB := m["missing"]
check(a == b && okA && !okB, "presence")
```

**Expected:** The edited run panics with `presence` because `a == b && okA && !okB` no longer holds.

**Verify:** Restoring `m := map[string]int{"zero": 0}` makes the check pass again with the worked observation: both values are 0, but only zero is present.

A numeric value alone cannot represent both absence and an intentional zero without losing information.

## 2. Build a frequency table: debug a regression

A one-token regression in worked example 2 makes a line read `for _, v := range []string{"red!", "blue", "red"} {`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
m := map[string]int{}
for _, v := range []string{"red", "blue", "red"} {
	m[v]++
}
check(m["red"] == 2 && m["blue"] == 1, "counts")
```

**Expected:** The defective run panics with `counts`; after restoring `for _, v := range []string{"red", "blue", "red"} {`, red has count 2 and blue has count 1.

**Verify:** The failing run shows message `counts`; after the repair `m["red"] == 2 && m["blue"] == 1` holds again.

Missing counts start at the zero value, which is useful here because zero is the correct additive identity.

## 3. Sort report keys

Extract keys beta and alpha and sort them.

```go
m := map[string]int{"beta": 2, "alpha": 1}
keys := []string{}
for k := range m {
	keys = append(keys, k)
}
sort.Strings(keys)
check(keys[0] == "alpha" && keys[1] == "beta", "sorted keys")
```

**Expected:** The first output key is alpha.

**Verify:** Your solution must keep `keys[0] == "alpha" && keys[1] == "beta"` true. Control: changing `check(keys[0] == "alpha" && keys[1] == "beta", "sorted keys")` to `check(keys[1] == "alpha" && keys[1] == "beta", "sorted keys")` panics with message `sorted keys`; revert it.

Sorting makes the presentation contract explicit. Repeatedly observing one map order never makes it guaranteed.

## 4. Observe assigned map aliasing

Assign a map to another variable and update through the second.

```go
a := map[string]int{"x": 1}
b := a
b["x"] = 2
check(a["x"] == 2, "map alias")
```

**Expected:** Both names observe the changed entry.

**Verify:** Your solution must keep `a["x"] == 2` true. Control: changing `b["x"] = 2` to `b["x"] = 3` panics with message `map alias`; revert it.

The assignment does not recursively clone map entries. Independent snapshots require a deliberate copy and a policy for nested mutable values.

## 5. Remove an absent key safely

Delete a missing key and then an existing key.

```go
m := map[string]int{"x": 1}
delete(m, "absent")
delete(m, "x")
check(len(m) == 0, "delete")
```

**Expected:** The map ends empty without a failure.

**Verify:** Your solution must keep `len(m) == 0` true. Control: changing `m := map[string]int{"x": 1}` to `m := map[string]int{"x!": 1}` panics with message `delete`; revert it.

Idempotent deletion is helpful for cleanup: repeating the same intent does not introduce a new error for an already absent entry.

## 6. Transfer nil read behavior

Read a missing key from a nil map.

```go
var m map[string]int
v, ok := m["x"]
check(v == 0 && !ok, "nil read")
```

**Expected:** The value is 0 and presence is false.

**Verify:** Your solution must keep `v == 0 && !ok` true. Control: changing `check(v == 0 && !ok, "nil read")` to `check(v != 0 && !ok, "nil read")` panics with message `nil read`; revert it.

This safe read does not mean a nil map is writable. Initialize storage before assignment instead of using a panic as ordinary control flow.

## Transfer after comparison

A map read answers two questions, the stored value and whether the key exists, and only the comma-ok form keeps both. Order and concurrency work the same way: Go provides neither, so the code must add them. When later lessons build caches, label selectors and configuration overlays, decide explicitly how a missing key differs from a zero value and how output order is made deterministic.

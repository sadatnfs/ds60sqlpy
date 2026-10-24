# go-006: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A map associates keys with values. Reading an absent key returns the value type's zero value, which can be indistinguishable from a present key whose value is zero. The comma-ok form retains the presence information. Map iteration order is deliberately unspecified; reproducible reports must extract and sort keys rather than rely on an observed order. Maps share mutable storage when assigned, and ordinary maps are not safe for concurrent mutation without synchronization. A nil map can be read but cannot accept an assignment. Treat these properties as part of the data model when building counters, caches and configuration overlays.

map[string]int declares string keys and integer values. value, ok := counts[key] distinguishes absence from zero. make initializes writable map storage. delete removes a key and is harmless if the key is absent. range gives key/value pairs in an unspecified order. Use sort.Strings on extracted keys before producing ordered output.

## 1. Distinguish zero from missing

Read present key zero and absent key missing with comma-ok.

```go
m := map[string]int{"zero": 0}
a, okA := m["zero"]
b, okB := m["missing"]
check(a == b && okA && !okB, "presence")
```

**Expected:** Both values are 0, but only zero is present.

A numeric value alone cannot represent both absence and an intentional zero without losing information.

## 2. Build a frequency table

Count red, blue and red.

```go
m := map[string]int{}
for _, v := range []string{"red", "blue", "red"} {
	m[v]++
}
check(m["red"] == 2 && m["blue"] == 1, "counts")
```

**Expected:** red has count 2 and blue has count 1.

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

Idempotent deletion is helpful for cleanup: repeating the same intent does not introduce a new error for an already absent entry.

## 6. Transfer nil read behavior

Read a missing key from a nil map.

```go
var m map[string]int
v, ok := m["x"]
check(v == 0 && !ok, "nil read")
```

**Expected:** The value is 0 and presence is false.

This safe read does not mean a nil map is writable. Initialize storage before assignment instead of using a panic as ordinary control flow.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

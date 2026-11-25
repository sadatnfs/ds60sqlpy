# java-008: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

A record is a concise carrier for a fixed set of components, with generated accessors, equality, hashing and a descriptive string. It is shallowly immutable: the component references cannot be reassigned, but a mutable object referenced by a component can still change. A compact constructor can validate and normalize incoming component values before the record is created. Defensive copying is necessary when the record owns a collection. Constructor validation should reject invalid domain state consistently, so every successfully created value can be trusted to satisfy its invariant. Records are appropriate for value-like data, not a substitute for every stateful object.

**Record:** A value-oriented class with declared components and generated methods.

**Compact constructor:** Validation and normalization code for record components.

**Defensive copy:** An owned copy preventing external mutation through shared storage.

## Reading the reference

record Order(String id, List<String> items) declares component accessors id() and items(). In a compact constructor, assign a normalized parameter such asid=id.strip(); implicit field assignment occurs afterward. List.copyOf makes an unmodifiable shallow copy, preventing later structural changes through the caller list. It also rejects null elements, which becomes part of the chosen contract.

## Exercise 1: Normalize at construction: change one input

Task: Change `Order order = new Order(" A ", List.of("x"));` to `Order order = new Order(" A !", List.of("x"));` in Example A and predict which assertion fails and why.

Normalization occurs once at the boundary. Every later accessor sees the canonical ID, rather than requiring callers to remember to trim it.

The unchanged code is the part that Example A adds:

```java
Order order = new Order(" A ", List.of("x"));
assert order.id().equals("A") && order.items().equals(List.of("x"));
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `order.id().equals("A") && order.items().equals(List.of("x"))`.

**Verify:** Name the value that makes `order.id().equals("A") && order.items().equals(List.of("x"))` false, then restore the line.

## Exercise 2: Copy caller-owned collections: debug a regression

Task: A regression in Example B's new code makes one line read `List<String> supplied = new ArrayList<>(List.of("x!"));`. Repair it using the failing assertion.

Without the copy, a caller could change the record observed value after construction. Final component references alone would not prevent that mutation.

The unchanged code is the part that Example B adds:

```java
List<String> supplied = new ArrayList<>(List.of("x"));
Order copied = new Order("B", supplied);
supplied.add("y");
assert copied.items().equals(List.of("x"));
```

**Expected:** The unrepaired run fails with an `AssertionError` from the assertion on `copied.items().equals(List.of("x"))`; the repaired line reads `List<String> supplied = new ArrayList<>(List.of("x"));`.

**Verify:** Explain how the changed token alters the value that `copied.items().equals(List.of("x"))` tests.

## Exercise 3: Use value equality

Task: Construct another Order with normalized A and item x.

Record equality compares component values. This is useful for stable data carriers and differs from default object identity equality.

```java
Order same = new Order("A", List.of("x"));
assert order.equals(same) && order.hashCode() == same.hashCode();
```

**Expected:** equals true and equal hashCode.

**Verify:** Control: changing `Order same = new Order("A", List.of("x"));` to `Order same = new Order("A!", List.of("x"));` must fail the assertion on `order.equals(same) && order.hashCode() == same.hashCode()`.

## Exercise 4: Reject blank identity

Task: Construct an Order with an all-space ID.

A syntactically valid String can still violate a domain invariant. Validate after normalization so whitespace-only values cannot slip through.

```java
boolean blank = false;
try {
  new Order("  ", List.of("x"));
} catch (IllegalArgumentException expected) {
  blank = true;
}
assert blank;
```

**Expected:** IllegalArgumentException.

**Verify:** Control: changing `blank = true;` to `blank = false;` must fail the assertion on `blank`.

## Exercise 5: Protect the exposed collection

Task: Attempt to add to order.items().

The accessor returns the owned unmodifiable list. If its elements were mutable objects, their internal state would still need separate treatment.

```java
boolean protectedItems = false;
try {
  order.items().add("z");
} catch (UnsupportedOperationException expected) {
  protectedItems = true;
}
assert protectedItems;
```

**Expected:** UnsupportedOperationException.

**Verify:** Control: changing `protectedItems = true;` to `protectedItems = false;` must fail the assertion on `protectedItems`.

## Exercise 6: Reject null collection members

Task: Try creating an Order whose items contains null.

The constructor uses List.copyOf, whose null policy is explicit. An alternative domain could allow missing items, but should encode that meaning instead of accidentally accepting null.

```java
boolean nullItem = false;
try {
  new Order("C", Arrays.asList("x", null));
} catch (NullPointerException expected) {
  nullItem = true;
}
assert nullItem;
```

**Expected:** NullPointerException from the declared copy policy.

**Verify:** Control: changing `nullItem = true;` to `nullItem = false;` must fail the assertion on `nullItem`.

## After comparing the answer

Add a `withItem(String item)` method to your copy that returns a new `Order` instead of mutating, and confirm that the original record still has one item.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.

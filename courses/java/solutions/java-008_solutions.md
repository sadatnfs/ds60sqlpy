# java-008: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

A record is a concise carrier for a fixed set of components, with generated accessors, equality, hashing and a descriptive string. It is shallowly immutable: the component references cannot be reassigned, but a mutable object referenced by a component can still change. A compact constructor can validate and normalize incoming component values before the record is created. Defensive copying is necessary when the record owns a collection. Constructor validation should reject invalid domain state consistently, so every successfully created value can be trusted to satisfy its invariant. Records are appropriate for value-like data, not a substitute for every stateful object.

**Record:** A value-oriented class with declared components and generated methods.

**Compact constructor:** Validation and normalization code for record components.

**Defensive copy:** An owned copy preventing external mutation through shared storage.

## Reading the reference

record Order(String id,List<String>items) declares component accessorsid() and items(). In a compact constructor, assign a normalized parameter such asid=id.strip(); implicit field assignment occurs afterward. List.copyOf makes an unmodifiable shallow copy, preventing later structural changes through the caller list. It also rejects null elements, which becomes part of the chosen contract.

## Exercise 1: Normalize at construction

Task: Create an Order with ID " A " and item x.

Normalization occurs once at the boundary. Every later accessor sees the canonical ID, rather than requiring callers to remember to trim it.

```java
Order order = new Order(" A ", List.of("x"));
assert order.id().equals("A") && order.items().equals(List.of("x"));
```

**Expected:** ID A and items[x].

**Verify:** Compare the program values or named exception with ID A and items[x]. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Copy caller-owned collections

Task: Create an Order from a mutable list,then append to the original list.

Without the copy, a caller could change the record observed value after construction. Final component references alone would not prevent that mutation.

```java
List<String> supplied = new ArrayList<>(List.of("x")); Order copied = new Order("B", supplied); supplied.add("y");
assert copied.items().equals(List.of("x"));
```

**Expected:** record retains its original single item.

**Verify:** Compare the program values or named exception with record retains its original single item. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Use value equality

Task: Construct another Order with normalizedA and item x.

Record equality compares component values. This is useful for stable data carriers and differs from default object identity equality.

```java
Order same = new Order("A", List.of("x"));
assert order.equals(same) && order.hashCode() == same.hashCode();
```

**Expected:** equals true and equalhashCode.

**Verify:** Compare the program values or named exception with equals true and equalhashCode. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Reject blank identity

Task: Construct an Order with an all-space ID.

A syntactically valid String can still violate a domain invariant. Validate after normalization so whitespace-only values cannot slip through.

```java
boolean blank = false;
try { new Order("  ", List.of("x")); } catch (IllegalArgumentException expected) { blank = true; }
assert blank;
```

**Expected:** IllegalArgumentException.

**Verify:** Compare the program values or named exception with IllegalArgumentException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Protect the exposed collection

Task: Attempt to add toorder.items().

The accessor returns the owned unmodifiable list. If its elements were mutable objects, their internal state would still need separate treatment.

```java
boolean protectedItems = false;
try { order.items().add("z"); } catch (UnsupportedOperationException expected) { protectedItems = true; }
assert protectedItems;
```

**Expected:** UnsupportedOperationException.

**Verify:** Compare the program values or named exception with UnsupportedOperationException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject null collection members

Task: Try creating an Order whose items contains null.

The constructor usesList.copyOf, whose null policy is explicit. An alternative domain could allow missing items, but should encode that meaning instead of accidentally accepting null.

```java
boolean nullItem = false;
try { new Order("C", Arrays.asList("x", null)); } catch (NullPointerException expected) { nullItem = true; }
assert nullItem;
```

**Expected:** NullPointerException from the declared copy policy.

**Verify:** Compare the program values or named exception with NullPointerException from the declared copy policy. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.

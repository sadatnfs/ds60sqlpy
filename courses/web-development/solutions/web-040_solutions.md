# web-040: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-040.md`.

## Exercise 1: Name the invariant enforced by the constructor.

**Expected answer:** A successfully constructed duration cannot begin with negative minutes.

**Why:** Because the constructor throws for negative minutes and the property is readonly, every Duration object has nonnegative minutes for its whole life.

## Exercise 2: Add a method that formats the duration.

**Expected evidence:** Formatting derives from state without changing it.

**Why:** A method that only reads state keeps the object immutable and the formatting reusable.

## Exercise 3: Build a validated study-session value object.

**Expected evidence:** Its topic and duration satisfy explicit constructor checks and remain readonly.

**Why:** Constructor validation plus readonly properties mean invalid sessions cannot be created or changed later.

## Exercise 4: Diagnose a setter that allows invalid state after construction.

**Expected answer:** Every mutation boundary must preserve the invariant, or mutation should be removed.

**Why:** A setter without the constructor's checks lets invalid state in later, so it must validate the same rule or be removed.

## Exercise 5: Test an empty topic and zero duration.

**Expected evidence:** The topic is rejected while zero follows the declared nonnegative policy.

**Why:** The empty topic violates the rule and throws, while zero minutes satisfies the nonnegative rule.

## Exercise 6: Explain shallow readonly versus deep immutability.

**Expected answer:** A readonly property cannot be reassigned, but referenced mutable objects can have their own changing state.

**Why:** readonly prevents reassigning the property but not mutating the object it refers to, so deep immutability needs immutable members too.

## Reference comparison

Open `courses/web-development/solutions/web-040_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.

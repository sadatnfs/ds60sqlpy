# web-040: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-040.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Name the invariant enforced by the constructor.

**Expected answer:** A successfully constructed duration cannot begin with negative minutes.

**Approach:** Read the constructor check and state its guarantee: any `Duration` that exists was created with minutes of zero or more.

**Why:** Because the constructor throws for negative minutes and the property is readonly, every Duration object has nonnegative minutes for its whole life.

**Plausible wrong approach:** Saying the check makes `minutes` unchangeable fails because that comes from `readonly`, while the check only guards the starting value.

**How to verify:** `new Duration(-1)` throws InvalidArgumentException and `new Duration(0)` succeeds. Trying `$d->minutes = 5` afterward throws an Error, which is the separate readonly guarantee.

## Exercise 2: Add a method that formats the duration.

**Expected evidence:** Formatting derives from state without changing it.

**Approach:** Add `public function label(): string` that returns the minutes with a unit, reading `$this->minutes` without assigning to it.

**Why:** A method that only reads state keeps the object immutable and the formatting reusable.

**Plausible wrong approach:** Storing the label in a second property fails because a future change to minutes could leave the label out of date.

**How to verify:** Calling `label()` twice returns 45 minutes both times, and minutes is still 45.

## Exercise 3: Build a validated study-session value object.

**Expected evidence:** Its topic and duration satisfy explicit constructor checks and remain readonly.

**Approach:** Promote `string $topic` and `int $minutes` as readonly, trim and reject an empty topic, and reject negative minutes in the constructor.

**Why:** Constructor validation plus readonly properties mean invalid sessions cannot be created or changed later.

**Plausible wrong approach:** Validating in a separate `isValid()` method fails because callers can construct and use an invalid object without calling it.

**How to verify:** Each invalid input throws during `new`, and the valid object shows both fields unchanged after use. A topic of three spaces is rejected too, because the constructor trims before checking for empty text.

## Exercise 4: Diagnose a setter that allows invalid state after construction.

**Expected answer:** Every mutation boundary must preserve the invariant, or mutation should be removed.

**Approach:** Remove the setter or make it validate with the same rule as the constructor before assigning the new value.

**Why:** A setter without the constructor's checks lets invalid state in later, so it must validate the same rule or be removed.

**Plausible wrong approach:** Keeping a public setter with no check fails because any caller can set minutes to -10 after construction.

**How to verify:** After the repair, no public method can leave minutes below zero, as a test of each method shows. Searching the class for assignments to `$this->minutes` finds only the constructor, or a setter that repeats the check.

## Exercise 5: Test an empty topic and zero duration.

**Expected evidence:** The topic is rejected while zero follows the declared nonnegative policy.

**Approach:** Construct with an empty topic and with zero minutes, catching the expected exception for the first one.

**Why:** The empty topic violates the rule and throws, while zero minutes satisfies the nonnegative rule.

**Plausible wrong approach:** Treating zero minutes as invalid fails because the stated policy is nonnegative, which includes zero.

**How to verify:** The empty topic throws InvalidArgumentException, while zero minutes creates a valid object. Printing the zero minute object's `label()` shows 0 minutes, matching the documented nonnegative rule.

## Exercise 6: Explain shallow readonly versus deep immutability.

**Expected answer:** A readonly property cannot be reassigned, but referenced mutable objects can have their own changing state.

**Approach:** Explain that readonly blocks reassignment of the property but not changes inside an object it refers to.

**Why:** readonly prevents reassigning the property but not mutating the object it refers to, so deep immutability needs immutable members too.

**Plausible wrong approach:** Claiming a readonly `ArrayObject` property makes the list unchangeable fails because appending items still works.

**How to verify:** In the contrast case, the append succeeds and count prints 2, while reassignment throws an Error. Copying the input into a plain readonly array property instead makes both the append and the reassignment fail.

## Reference comparison

The reference requires the label to read CSS: 45 minutes and requires an empty topic to throw InvalidArgumentException. That catches a wrong format and a missing guard. It does not test zero or negative minutes or attempt a mutation, so add those checks yourself.

Open `courses/web-development/solutions/web-040_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).

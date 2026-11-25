# swift-014: explanation and comparison

Reference program: [swift-014_solution.swift](swift-014_solution.swift), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Derive instead of duplicating:** One source of truth prevents stale duplicated state. Area changes with width without a separately updated area field.

**Expose a conversion property:** A computed property can expose a convenient representation while retaining one stored unit. The getter and setter translate between temperature scales.

## Task answers

### Task 1: Predict and explain

Trace which properties are stored and which are derived.

**Reference answer.** It runs as the `Task 1` block of the reference program.

```swift
let rectangleFields = Mirror(reflecting: Rectangle(width: 3, height: 4)).children
precondition(rectangleFields.map(\.label) == ["width", "height"])
let temperatureFields = Mirror(reflecting: Temperature(celsius: 0)).children
precondition(temperatureFields.map(\.label) == ["celsius"])
```

**Observe:** Rectangle stores only width and height, and Temperature stores only celsius.

Mirror lists stored properties; area and fahrenheit are absent because they are computed from the stored values every time they are read.

### Task 2: Guided modification

Add a computed rectangle perimeter.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```swift
var rectangle = Rectangle(width: 3, height: 4)
precondition(rectangle.perimeter == 14)
rectangle.width = 5
precondition(rectangle.perimeter == 18)
```

**Observe:** The perimeter is 14 for 3 by 4 and 18 after the width becomes 5.

A computed property added in an extension needs no storage, so it follows width without any update code.

### Task 3: Independent construction

Build a value model with one stored unit and a documented converted view.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
/// Stores meters only; feet is a derived view and is never stored.
struct Length {
  var meters: Double
  var feet: Double { meters / 0.3048 }
}
let length = Length(meters: 3.048)
precondition(abs(length.feet - 10) < 1e-9)
```

**Observe:** 3.048 meters reads as 10 feet.

With a single stored unit there is nothing to keep in sync; the converted value is computed from meters every time it is read.

### Task 4: Diagnose a defect

Diagnose a separately stored area that is not updated after width changes.

**Reference answer.** It runs as the `Task 4` block of the reference program.

```swift
struct StaleRectangle {
  var width: Int
  var height: Int
  var area: Int
}
var stale = StaleRectangle(width: 3, height: 4, area: 12)
stale.width = 5
precondition(stale.area == 12)
var derived = Rectangle(width: 3, height: 4)
derived.width = 5
precondition(derived.area == 20)
```

**Observe:** After widening to 5 the stored area still says 12, while the computed area says 20.

A stored copy of derived data must be updated by every writer; nothing updates stale.area, so it goes out of date. Computing area removes that obligation.

### Task 5: Boundary evidence

Test zero and a non-integer conversion case.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```swift
precondition(Rectangle(width: 0, height: 4).area == 0)
var temperature = Temperature(celsius: 0)
precondition(temperature.fahrenheit == 32)
temperature.celsius = 37.5
precondition(abs(temperature.fahrenheit - 99.5) < 1e-9)
temperature.fahrenheit = 98.6
precondition(abs(temperature.celsius - 37) < 1e-9)
```

**Observe:** A zero width gives area 0; 0 C is 32 F, 37.5 C is 99.5 F, and setting 98.6 F stores 37 C.

37.5 * 9 / 5 + 32 is 99.5, and (98.6 - 32) * 5 / 9 is 37; 98.6 is not exact in binary, so the tolerance compares the conversion rather than exact bits.

### Task 6: Transfer and justify

Choose an explicit method instead of a setter for a state change with validation and failure.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Solution reasoning

**Approach.** Example A computes `area` from stored `width` and `height` instead of storing it. Example B stores only `celsius` and exposes `fahrenheit` as a computed property with a getter and setter. The task 3 answer stores meters and exposes a converted feet view.

**Why it is correct.** Because area is computed on every read, changing width from 3 to 5 changes area from 12 to 20 with no update code. The Fahrenheit getter applies `celsius * 9 / 5 + 32`, giving 32 at 0, and the setter inverts it, so assigning 212 stores a Celsius value within 1e-9 of 100. In task 3, 3.048 meters reads as 10 feet.

**A plausible wrong approach.** Storing `area` as a separate field initialized to 12 is the stale-state trap: after `rectangle.width = 5`, area still reads 12 and the second check fails. Comparing the converted Celsius with `== 100` instead of a tolerance can also fail, because floating division may leave a tiny residue.

**How to verify.** Add `var perimeter: Int { 2 * (width + height) }` for task 2 and check it is 14 for 3 by 4 and 18 after width becomes 5. For task 5, check that 37.5 Celsius reads as 99.5 Fahrenheit.

## Mechanism and diagnostic reasoning

A stored property retains data; a computed property derives a value from other state. Prefer deriving cheap dependent values instead of storing duplicates that can disagree. A property observer reacts to a stored-value change but should not become an invisible substitute for a clear domain operation.

Computed setters translate an external representation back into stored state. That translation may lose information, so document it. Access control can permit reading without external writing. Property wrappers later package reusable access behavior, but start by understanding the plain getter and setter contract.

`var area: Int { width * height }` computes a value. `get` and `set` define two-way access; newValue names the assigned value. didSet observes assignments after the new value is stored.

Expensive computed properties can surprise callers who expect cheap access. Observers can hide cascading side effects. Avoid duplicating state unless there is a measured caching need and invalidation policy.

## Review before continuing

Run the reference and confirm it prints `swift-014: passed`, then rerun the guide's counterexample.

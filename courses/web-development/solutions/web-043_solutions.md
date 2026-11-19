# web-043: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-043.md`.

## Exercise 1: Explain an instant versus a local clock reading.

**Expected answer:** An instant is a timeline point; a local reading needs zone context and can be ambiguous.

**Why:** An instant is one point on the timeline, while a local clock reading needs a time zone and can be ambiguous or nonexistent around clock changes.

## Exercise 2: Convert a fixed instant to a named time zone.

**Expected evidence:** The displayed hour changes but the Unix timestamp remains equal.

**Why:** setTimezone changes only the display zone; the instant and its Unix timestamp stay the same.

## Exercise 3: Build a deterministic study-session time report.

**Expected evidence:** The output uses explicit time zones and a fixed input suitable for repeatable tests.

**Why:** Fixed inputs make the report repeatable, so tests do not depend on when they run.

## Exercise 4: Diagnose a test that fails around midnight.

**Expected answer:** Replace ambient current time with a controlled clock or input.

**Why:** Code that reads the current time behaves differently near midnight, so a controlled clock or fixed input makes it deterministic.

## Exercise 5: Compare elapsed seconds with a calendar-day operation near a clock change.

**Expected answer:** They can represent different elapsed durations; document which the application intends.

**Why:** A calendar day can be 23 or 25 hours long around a clock change, so the application must say which meaning it needs.

## Exercise 6: Explain why a numeric offset is not a complete regional time-zone rule.

**Expected answer:** A region can change offsets over time due to daylight saving or policy changes.

**Why:** An offset such as -05:00 is fixed, while a region like America/New_York changes offsets with daylight saving and policy.

## Reference comparison

Open `courses/web-development/solutions/web-043_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.

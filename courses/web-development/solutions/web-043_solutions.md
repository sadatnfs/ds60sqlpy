# web-043: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-043.md`.

## Exercise 1: Explain an instant versus a local clock reading.

**Expected answer:** An instant is a timeline point; a local reading needs zone context and can be ambiguous.

**Approach:** Describe an instant as one point on the global timeline, and a local reading as a date and clock value that needs a zone to locate it.

**Why:** An instant is one point on the timeline, while a local clock reading needs a time zone and can be ambiguous or nonexistent around clock changes.

**Plausible wrong approach:** Treating 2024-03-10 02:30 in New York as a real instant fails because that local time was skipped when clocks moved forward.

**How to verify:** Two different zones show different local readings for one instant, and `getTimestamp()` returns the same number for both.

## Exercise 2: Convert a fixed instant to a named time zone.

**Expected evidence:** The displayed hour changes but the Unix timestamp remains equal.

**Approach:** Call `setTimezone` on the immutable instant with a named zone and format the result with the offset included.

**Why:** setTimezone changes only the display zone; the instant and its Unix timestamp stay the same.

**Plausible wrong approach:** Using `modify('-5 hours')` to convert fails because it changes the instant itself, and the offset differs in summer.

**How to verify:** The converted value prints 2024-01-01 07:00 -05:00, and `getTimestamp()` equals the UTC original.

## Exercise 3: Build a deterministic study-session time report.

**Expected evidence:** The output uses explicit time zones and a fixed input suitable for repeatable tests.

**Approach:** Accept the session start as a fixed string with an offset, convert it to the learner's named zone, and print both readings.

**Why:** Fixed inputs make the report repeatable, so tests do not depend on when they run.

**Plausible wrong approach:** Calling `new DateTimeImmutable('now')` inside the report fails because each run then prints a different time and tests cannot compare.

**How to verify:** Running the report twice prints identical lines, each with an explicit offset or zone name.

## Exercise 4: Diagnose a test that fails around midnight.

**Expected answer:** Replace ambient current time with a controlled clock or input.

**Approach:** Pass the current time into the function as a parameter, and supply a fixed instant from the test.

**Why:** Code that reads the current time behaves differently near midnight, so a controlled clock or fixed input makes it deterministic.

**Plausible wrong approach:** Rerunning the test after midnight to make it pass fails because the hidden dependency on the real clock remains.

**How to verify:** The test passes when you change the system clock, because it never reads the real current time.

## Exercise 5: Compare elapsed seconds with a calendar-day operation near a clock change.

**Expected answer:** They can represent different elapsed durations; document which the application intends.

**Approach:** Run both operations from the contrast case, then compute the elapsed seconds between the start and each result.

**Why:** A calendar day can be 23 or 25 hours long around a clock change, so the application must say which meaning it needs.

**Plausible wrong approach:** Assuming every calendar day is 86400 seconds fails because days that include a clock change are 23 or 25 hours.

**How to verify:** The calendar step gives 82800 seconds elapsed, while the timestamp step gives 86400.

## Exercise 6: Explain why a numeric offset is not a complete regional time-zone rule.

**Expected answer:** A region can change offsets over time due to daylight saving or policy changes.

**Approach:** Store a region name such as America/New_York and let the time zone database supply the offset for each date.

**Why:** An offset such as -05:00 is fixed, while a region like America/New_York changes offsets with daylight saving and policy.

**Plausible wrong approach:** Storing -05:00 as the learner's zone fails because summer dates in that region use -04:00.

**How to verify:** Formatting a July and a January date in the named zone prints -04:00 and -05:00 respectively.

## Reference comparison

Open `courses/web-development/solutions/web-043_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.

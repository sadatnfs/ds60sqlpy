# js-035: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A date-time problem can involve an instant, a calendar date, a local clock reading or a duration. These are different concepts. JavaScript Date primarily represents a millisecond offset from the Unix epoch. Its display can use a timezone, but the object does not retain an original timezone label. Two ISO strings with different offsets can identify the same instant. A business date such as a billing day may need a separate calendar-date representation rather than an invented midnight instant.

Parsing is part of the contract. Accepting arbitrary date text lets implementation and locale assumptions enter the program. This lesson accepts an explicit YYYY-MM-DD format for calendar dates and verifies that the constructed UTC date round-trips to the same components. That rejects impossible dates that a permissive construction could normalize into another month. Invalid Date is still a Date object, so instanceof alone does not establish a valid timestamp.

Timezones map instants to local civil times. During a spring daylight-saving transition, some local clock readings do not occur. During a fall transition, the same local reading can correspond to two different instants. Adding 24 elapsed hours is not always the same as advancing a local calendar day at the same wall-clock time. The fixtures use specified UTC instants and named America/New_York rules, avoiding dependence on the host's default timezone.

Intl formats values according to an explicit locale and timezone. Prefer formatToParts when inspecting semantic fields rather than assuming punctuation, spacing or ordering. Formatting is not general parsing. Calendar and locale data can change across runtime versions; report the prepared runtime and avoid inferring a universal parser from one formatted string.

**Instant:** A specific point on the timeline.

**Calendar date:** A year-month-day value without an implied instant.

**Timezone:** Rules mapping instants to local calendar and clock fields.

**Locale formatting:** Displaying values under language and regional conventions.

## Reading the implementation

Date.parse on an ISO string with Z or an explicit offset produces an instant. toISOString produces UTC text. Number.isFinite(date.getTime()) checks timestamp validity. Intl.DateTimeFormat accepts timeZone and hourCycle explicitly; formatToParts returns named fields. Intl.NumberFormat separates display conventions from numeric storage. Integer cents should remain integer cents while formatting a display value under a declared currency and rounding policy.

## Exercise 1: Compare offset spellings of one instant: change one input

Task: In a scratch copy of Example A, change `const utc = new Date('2024-01-01T00:00:00Z');` to `const utc = new Date('2025-01-01T00:00:00Z');`. Which check fails, and what value does it see?

The offset changes the written clock reading, not the represented instant. Date does not preserve the original -05:00 label as part of its identity.

The unchanged code is the exercise block of Example A:

```javascript
const utc = new Date('2024-01-01T00:00:00Z');
const offset = new Date('2023-12-31T19:00:00-05:00');
assert.equal(utc.getTime(), offset.getTime());
assert.equal(offset.toISOString(), '2024-01-01T00:00:00.000Z');
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(utc.getTime(), offset.getTime())`. Restoring `const utc = new Date('2024-01-01T00:00:00Z');` brings back: equal timestamps and UTC ISO output.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const utc = new Date('2024-01-01T00:00:00Z');`.

## Exercise 2: Observe a spring-forward clock gap: diagnose an edited check

Task: Example B's check was edited to read `assert.equal(after.getTime() + before.getTime(), 60 * 60 * 1000);`. Run it, explain the failure and restore the original.

The timeline remains continuous while local civil labels skip an hour. A local scheduling problem must account for this mapping rather than assuming every day contains every clock reading.

The unchanged code is the exercise block of Example B:

```javascript
const before = new Date('2024-03-10T06:30:00Z');
const after = new Date('2024-03-10T07:30:00Z');
assert.equal(parts(before).hour, '01');
assert.equal(parts(after).hour, '03');
assert.equal(after.getTime() - before.getTime(), 60 * 60 * 1000);
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.equal(after.getTime() + before.getTime(), 60 * 60 * 1000);`. Restoring `assert.equal(after.getTime() - before.getTime(), 60 * 60 * 1000);` brings back: local hour changes from 01 to 03 while elapsed time is one hour.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Reject impossible or ambiguous calendar text

Task: Accept leap-day 2024-02-29 and reject 2023-02-29, slash format and month 13.

A round-trip component check catches normalization of impossible dates. A strict grammar avoids choosing a day/month interpretation from host locale.

```javascript
assert.equal(calendarDate('2024-02-29'), '2024-02-29');
for (const text of ['2023-02-29', '01/02/2024', '2024-13-01'])
  assert.throws(() => calendarDate(text), RangeError);
```

**Expected:** only the valid strict date is accepted.

**Verify:** Keep `assert.throws(() => calendarDate(text), RangeError)`. Control: changing `for (const text of ['2023-02-29', '01/02/2024', '2024-13-01'])` to `for (const text of ['2024-02-29', '01/02/2024', '2024-13-01'])` must make that check fail; then restore it.

## Exercise 4: Distinguish repeated fall-back clock readings

Task: Format two instants on either side of the fall transition.

A local clock label without an offset or disambiguation policy may not identify one instant. Persisting only that label loses information.

```javascript
const first = new Date('2024-11-03T05:30:00Z');
const second = new Date('2024-11-03T06:30:00Z');
assert.equal(parts(first).hour, '01');
assert.equal(parts(second).hour, '01');
assert.equal(parts(first).minute, parts(second).minute);
assert.notEqual(parts(first).timeZoneName, parts(second).timeZoneName);
assert.equal(second.getTime() - first.getTime(), 3600000);
```

**Expected:** both read 01:30 locally but offsets differ and timestamps are one hour apart.

**Verify:** Keep `assert.equal(second.getTime() - first.getTime(), 3600000)`. Control: editing it to `assert.equal(second.getTime() + first.getTime(), 3600000);` must make the check fail; then restore it.

## Exercise 5: Inspect locale number parts without parsing display text

Task: Format 1234.5 in US English and German and inspect their decimal separators.

The formatter changes presentation, not the stored number. Removing punctuation from a localized string is not a reliable general numeric parser.

```javascript
const value = 1234.5;
const us = new Intl.NumberFormat('en-US').formatToParts(value);
const de = new Intl.NumberFormat('de-DE').formatToParts(value);
assert.equal(us.find((part) => part.type === 'decimal').value, '.');
assert.equal(de.find((part) => part.type === 'decimal').value, ',');
assert.equal(value, 1234.5);
```

**Expected:** decimal dot versus comma; numeric value remains unchanged.

**Verify:** Keep `assert.equal(us.find((part) => part.type === 'decimal').value, '.')`. Control: editing it to `assert.equal(us.find(part => part.type !== 'decimal').value, '.');` must make the check fail; then restore it.

## Exercise 6: Reject invalid timestamp and timezone assumptions

Task: Inspect Invalid Date and request a nonexistent timezone.

Being a Date instance does not imply timestamp validity. Unsupported timezone configuration should be diagnosed explicitly rather than silently falling back to the host default.

```javascript
const invalid = new Date('not an ISO instant');
assert.equal(Number.isNaN(invalid.getTime()), true);
assert.throws(() => invalid.toISOString(), RangeError);
assert.throws(() => new Intl.DateTimeFormat('en-US', { timeZone: 'Invalid/Nowhere' }), RangeError);
```

**Expected:** NaN timestamp; toISOString and invalid timezone construction throw RangeError.

**Verify:** Keep `assert.equal(Number.isNaN(invalid.getTime()), true)`. Control: editing it to `assert.equal(Number.isNaN(invalid.getTime()), false);` must make the check fail; then restore it.

## After comparison

Fresh case: count the days between local midnight on 2024-03-09 and 2024-03-11 in New York. Predict the result from timestamps divided by 86,400,000 and from calendar dates, and explain why they differ. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)

// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Compare offset spellings of one instant: change one input
// Copy Example A into a scratch `main.mjs` and change `const utc = new
// Date('2024-01-01T00:00:00Z');` to `const utc = new Date('2025-01-01T00:00:00Z');`. Before
// running it, predict which check fails and which value it now sees; then run it and restore
// the original line.
// Expected: The changed run fails with an `AssertionError` at `assert.equal(utc.getTime(),
// offset.getTime())`. Restoring `const utc = new Date('2024-01-01T00:00:00Z');` brings back:
// equal timestamps and UTC ISO output.

// Exercise 2: Observe a spring-forward clock gap: diagnose an edited check
// A careless edit changed a check in Example B so that it reads
// `assert.equal(after.getTime() + before.getTime(), 60 * 60 * 1000);`. Run Example B with
// that line, explain why the edited check now fails for the same program state, and restore
// it.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(after.getTime() + before.getTime(), 60 * 60 * 1000);`. Restoring
// `assert.equal(after.getTime() - before.getTime(), 60 * 60 * 1000);` brings back: local
// hour changes from 01 to 03 while elapsed time is one hour.

// Exercise 3: Reject impossible or ambiguous calendar text
// Accept leap-day 2024-02-29 and reject 2023-02-29, slash format and month 13.
// Expected: only the valid strict date is accepted.

// Exercise 4: Distinguish repeated fall-back clock readings
// Format two instants on either side of the fall transition.
// Expected: both read 01:30 locally but offsets differ and timestamps are one hour apart.

// Exercise 5: Inspect locale number parts without parsing display text
// Format 1234.5 in US English and German and inspect their decimal separators.
// Expected: decimal dot versus comma; numeric value remains unchanged.

// Exercise 6: Reject invalid timestamp and timezone assumptions
// Inspect Invalid Date and request a nonexistent timezone.
// Expected: NaN timestamp; toISOString and invalid timezone construction throw RangeError.

console.log("Implement the six exercises in your saved copy.");

// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Compare offset spellings of one instant
// Parse UTC midnight and the equivalent previous-day offset representation.
// Expected: equal timestamps and UTC ISO output.

// Exercise 2: Observe a spring-forward clock gap
// Format two instants one hour apart across the New York spring transition.
// Expected: local hour changes from 01 to 03 while elapsed time is one hour.

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

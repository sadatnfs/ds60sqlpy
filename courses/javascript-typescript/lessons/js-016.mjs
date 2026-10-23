// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Read a small UTF-8 file
// Write one line containing an emoji, then compare text length and byte length.
// Expected: text round-trips; UTF-8 byte length exceeds code-unit length.

// Exercise 2: Preserve characters and lines across chunks
// Stream two lines with a two-byte highWaterMark and decode using readline.
// Expected: lines are A😀B and second, without a corrupt replacement character.

// Exercise 3: Refuse accidental overwrite
// Create a file exclusively twice and inspect its unchanged content.
// Expected: second creation rejects with EEXIST; original first remains.

// Exercise 4: Distinguish a missing file
// Read a path known not to exist in the fresh directory.
// Expected: ENOENT rejection.

// Exercise 5: Restrict a learner-supplied fixture name
// Accept report.txt but reject traversal, separators and an absolute path.
// Expected: only report.txt is accepted.

// Exercise 6: Handle an empty text stream
// Stream an empty file with the same decoder and line interface.
// Expected: no lines.

console.log("Implement the six exercises in your saved copy.");

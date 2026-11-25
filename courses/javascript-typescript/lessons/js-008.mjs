// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Count code units and codepoints: predict an edited check
// In a scratch copy of Example A, change `assert.equal(text.codePointAt(1), 0x1f642);` to
// `assert.equal(text.codePointAt(2), 0x1f642);` inside its check. Does the check still pass?
// Expected: The edited run fails with an `AssertionError` at
// `assert.equal(text.codePointAt(2), 0x1f642);`. Restoring
// `assert.equal(text.codePointAt(1), 0x1f642);` brings back: length 3; spread count 2.

// Exercise 2: Compare canonical spellings: debug a regression
// A regression made one Example B line read `const composed = 'é!';`. Locate and repair it
// without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(decomposed.normalize('NFC'), composed)`. Restoring `const composed = 'é';`
// brings back: raw strings differ; normalized strings equal.

// Exercise 3: Match a literal regex fragment
// Escape a.b+ and match it exactly rather than interpreting dot and plus.
// Expected: literal accepted; axbb rejected.

// Exercise 4: Observe global regex cursor state
// Call /a/g repeatedly on aa and inspect lastIndex.
// Expected: matches at 0 then 1; third call false resets cursor 0.

// Exercise 5: Use Unicode-aware dot matching
// Compare `/^.$/` and `/^.$/u` on one emoji.
// Expected: without u false; with u true.

// Exercise 6: Bound a text-validation input
// Reject a string longer than 20 code units before applying an anchored ASCII identifier
// pattern.
// Expected: item_1 accepted; oversized input rejected.

console.log("Implement the six exercises in your saved copy.");

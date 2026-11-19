// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Count code units and codepoints: predict an edited check
// Copy Example A into a scratch `main.mjs` and change `assert.equal(text.codePointAt(1),
// 0x1f642);` to `assert.equal(text.codePointAt(2), 0x1f642);` inside its check. Before
// running it, predict whether the check still passes and explain why; then restore it.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(text.codePointAt(1), 0x1f642)`. Restoring the original line brings back the
// worked observation: length 3; spread count 2.

// Exercise 2: Compare canonical spellings: debug a regression
// A regression changed one token in Example B, so one line now reads `const composed =
// 'é!';`. Run Example B with that line, use the failing check to locate the defect and
// repair it without changing the check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.equal(decomposed.normalize('NFC'), composed)`; after it the line reads `const
// composed = 'é';` again and raw strings differ; normalized strings equal.

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

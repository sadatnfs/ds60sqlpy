// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Count code units and codepoints
// Inspect A followed by one emoji.
// Expected: length 3; spread count 2.

// Exercise 2: Compare canonical spellings
// Compare composed é with e plus combining acute before and after NFC.
// Expected: raw strings differ; normalized strings equal.

// Exercise 3: Match a literal regex fragment
// Escape a.b+ and match it exactly rather than interpreting dot and plus.
// Expected: literal accepted; axbb rejected.

// Exercise 4: Observe global regex cursor state
// Call /a/g repeatedly on aa and inspect lastIndex.
// Expected: matches at 0 then 1; third call false resets cursor 0.

// Exercise 5: Use Unicode-aware dot matching
// Compare /^.$/ and /^.$/u on one emoji.
// Expected: without u false; with u true.

// Exercise 6: Bound a text-validation input
// Reject a string longer than 20 code units before applying an anchored ASCII identifier
// pattern.
// Expected: item_1 accepted; oversized input rejected.

console.log("Implement the six exercises in your saved copy.");

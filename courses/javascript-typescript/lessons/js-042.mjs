// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Build, verify and execute a fresh bundle
// Create the authored bundle, verify hashes and run its self-test in a child.
// Expected: three checks passed; actual Node version reported.

// Exercise 2: Reject altered application bytes before execution
// Append a harmless comment to the owned application after manifest creation.
// Expected: digest verification fails.

// Exercise 3: Reject a manifest path outside the allowlist
// Replace one file entry with ../outside.txt.
// Expected: path is rejected before any outside file is read.

// Exercise 4: Preserve result and diagnostic channels on failure
// Invoke an unsupported argument containing a fake secret-like value.
// Expected: nonzero child exit; stdout empty; generic stderr without the value.

// Exercise 5: Derive stable content identity from unchanged files
// Read and hash the same app twice and compare with its manifest entry.
// Expected: equal digests and an unchanged manifest match.

// Exercise 6: Gate an observed runtime against explicit policy
// Accept the current runtime major for the fixture and reject a different required major.
// Expected: matching policy passes; mismatched policy throws.

console.log("Implement the six exercises in your saved copy.");

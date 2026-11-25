// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Build, verify and execute a fresh bundle: change one input
// In a scratch copy of Example A, change `const result = runBundle(directory, ['--self-
// test']);` to `const result = runBundle(directory, ['--self-test!']);`. Which check fails,
// and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(result.status, 0,
// result.stderr)`. Restoring `const result = runBundle(directory, ['--self-test']);` brings
// back: three checks passed; actual Node version reported.

// Exercise 2: Reject altered application bytes before execution: debug a regression
// A regression made one Example B line read `await appendFile(join(directory, 'app.mjs!'),
// '\n// controlled tamper fixture\n');`. Locate and repair it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.rejects(verifyBundle(directory), /digest mismatch/u)`. Restoring `await
// appendFile(join(directory, 'app.mjs'), '\n// controlled tamper fixture\n');` brings back:
// digest verification fails.

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

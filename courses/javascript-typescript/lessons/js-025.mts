// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Compile and run a two-module project: predict an edited check
// In a scratch copy of Example A, change `assert.equal(await exists(join(directory,
// 'compiled', 'math.mjs')), true);` to `assert.equal(await exists(join(directory,
// 'compiled!', 'math.mjs')), true);` inside its check. Does the check still pass?
// Expected: The edited run fails with an `AssertionError` at `assert.equal(await
// exists(join(directory, 'compiled!', 'math.mjs')), true);`. Restoring `assert.equal(await
// exists(join(directory, 'compiled', 'math.mjs')), true);` brings back: both processes
// succeed; output 8; math.mjs is emitted.

// Exercise 2: Inspect type-only erasure: debug a regression
// A regression made one Example B line read `'model.mts!': 'export type Item = { id: string
// };',`. Locate and repair it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr)`. Restoring
// `'model.mts': 'export type Item = { id: string };',` brings back: no model import in
// emitted entry; output A.

// Exercise 3: Reject a type mismatch without output
// Assign text to a number in a fresh project.
// Expected: TS2322; nonzero compiler status; no compiled main.mjs.

// Exercise 4: Require runtime-valid relative extensions
// Import ./math without an extension under NodeNext ESM.
// Expected: TS2835 and no emitted entry.

// Exercise 5: Observe a missing runtime artifact
// Compile successfully, remove only the owned emitted dependency, then run the entry.
// Expected: Node fails with ERR_MODULE_NOT_FOUND.

// Exercise 6: Retain value imports beside erased type imports
// Import both a type and a value from one module.
// Expected: value dependency remains; runtime prints ready:A.

console.log("Implement the six exercises in your saved copy.");

// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Compile and run a two-module project
// Compile a main module importing twice from ./math.mjs and run it.
// Expected: both processes succeed; output 8; math.mjs is emitted.

// Exercise 2: Inspect type-only erasure
// Compile a type import and inspect the emitted entry before running it.
// Expected: no model import in emitted entry; output A.

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

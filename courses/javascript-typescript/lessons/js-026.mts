// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Maintain balance through methods: change one input
// Copy Example A into a scratch `main.mts` and change `const wallet = new Wallet(100);` to
// `const wallet = new Wallet(101);`. Before running it, predict which check fails and which
// value it now sees; then run it and restore the original line.
// Expected: The changed run fails with an `AssertionError` at the check
// `assert.equal(wallet.cents, 120)`. Restoring the original line brings back the worked
// observation: balance 120; no enumerable balance field.

// Exercise 2: Inject a deterministic clock: debug a regression
// A regression changed one token in Example B, so one line now reads `const service = new
// ReceiptService({ now: () => new Date('2027-01-01T00:00:00.000Z') });`. Run Example B with
// that line, use the failing check to locate the defect and repair it without changing the
// check.
// Expected: Before the repair the run fails with an `AssertionError` at the check
// `assert.deepEqual(service.create('A'), { id: 'A', createdAt: '2026-01-01T00:00:00.000Z'
// })`; after it the line reads `const service = new ReceiptService({ now: () => new
// Date('2026-01-01T00:00:00.000Z') });` again and timestamp 2026-01-01T00:00:00.000Z.

// Exercise 3: Reject invalid transitions without mutation
// Try a negative deposit and an overdraw.
// Expected: both throw; balance stays 100.

// Exercise 4: Guard derived overflow
// Deposit one cent into the maximum safe balance.
// Expected: RangeError; original balance preserved.

// Exercise 5: Reject an incompatible collaborator
// Pass a clock returning text in an uncalled negative type check.
// Expected: expected compiler error; valid Date clock works.

// Exercise 6: Distinguish private storage from a lookalike property
// Add an ordinary balance property to the wallet.
// Expected: ordinary property 999; private cents remain 2.

console.log("Implement the six exercises in your saved copy.");

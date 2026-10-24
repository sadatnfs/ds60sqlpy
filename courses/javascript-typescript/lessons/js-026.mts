// Answer-free learner source. Save your own copy before editing.

export {};
// Exercise 1: Maintain balance through methods
// Start with 100 cents, deposit 50 and withdraw 30.
// Expected: balance 120; no enumerable balance field.

// Exercise 2: Inject a deterministic clock
// Create a receipt service using a fixed clock.
// Expected: timestamp 2026-01-01T00:00:00.000Z.

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

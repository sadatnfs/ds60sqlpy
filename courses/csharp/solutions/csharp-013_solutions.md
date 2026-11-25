# csharp-013: explanation and comparison

Reference program: [csharp-013_solution.cs](csharp-013_solution.cs), covering both examples.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Preserve a nonnegative balance:** Validate affordability before subtraction so rejected requests cannot corrupt state. Spending 4 succeeds; spending 7 afterward fails without changing 6.

**Reject malformed operations:** These are separate boundary policies. Both preserve the invariant, but they communicate different meanings to the caller. Negative spending is rejected and zero is an accepted no-op.

## Task answers

### Task 1: Predict and explain

Trace the wallet state through successful and rejected spending.

**Written answer.** `new Wallet(10)` starts at 10. `TrySpend(4)` passes both guards, subtracts and returns true, leaving 6. `TrySpend(7)` hits `amount > Balance` because 7 is greater than 6, returns false before subtraction, and the balance stays 6.

**Why it is correct.** The method runs its checks in order: malformed input throws, unaffordable input returns false, and only an accepted amount reaches `Balance -= amount`. A rejected call therefore exits before any state change.

**Plausible wrong approach.** Assuming `TrySpend(7)` takes the balance to -1 and then reports false misreads the order of statements. That would be the subtract-first defect from task 4, not the code shown.

**How to verify.** After the second call, check `wallet.Balance == 6` and then `wallet.TrySpend(6) && wallet.Balance == 0`. The `rejection retains balance` check and the new one both pass silently.

### Task 2: Guided modification

Add a validated deposit operation.

**Written answer.** Add `public void Deposit(int amount) { if (amount <= 0) throw new ArgumentOutOfRangeException(nameof(amount)); Balance += amount; }`. Check that depositing 5 into a wallet of 10 gives 15 and that `Deposit(-2)` throws with the balance still 15.

**Why it is correct.** The guard runs before the only mutation, so a malformed amount cannot lower the balance. Using the private setter keeps every change to `Balance` inside methods that validate first.

**Plausible wrong approach.** Validating with `if (Balance + amount < 0)` accepts `Deposit(-3)` on a balance of 10, turning a deposit into a hidden withdrawal of 3 that bypasses `TrySpend` entirely.

**How to verify.** Catch `ArgumentOutOfRangeException` around `Deposit(-2)` and check both that it was caught and that `Balance` is unchanged. Decide and test whether `Deposit(0)` is allowed; this answer rejects it.

### Task 3: Independent construction

Implement a bounded inventory whose reservations never make stock negative.

**Written answer.** Write `sealed class Inventory { public int Stock { get; private set; } public Inventory(int stock) { if (stock < 0) throw new ArgumentOutOfRangeException(nameof(stock)); Stock = stock; } public bool TryReserve(int quantity) { if (quantity <= 0) throw new ArgumentOutOfRangeException(nameof(quantity)); if (quantity > Stock) return false; Stock -= quantity; return true; } }`.

**Why it is correct.** The constructor establishes `Stock >= 0`, and `TryReserve` subtracts only after proving `quantity <= Stock`, so the result can never go negative. The private setter prevents callers from bypassing the check.

**Plausible wrong approach.** A public `Stock` property with a separate `Reserve` method lets a caller write `inventory.Stock -= 5` directly, so the invariant depends on every caller remembering the rule rather than on the class.

**How to verify.** With stock 3, check `TryReserve(2)` leaves 1, `TryReserve(2)` returns false with 1 left, and `TryReserve(1)` leaves 0. Wrap `TryReserve(0)` and `new Inventory(-1)` in `try` blocks expecting `ArgumentOutOfRangeException`.

### Task 4: Diagnose a defect

Diagnose subtracting before checking affordability.

**Written answer.** The defect is `Balance -= amount; if (Balance < 0) return false;`. With a balance of 6, `TrySpend(7)` sets `Balance` to -1 before returning false, so the rejected call has already corrupted the state. Move the comparison before the subtraction.

**Why it is correct.** Failure atomicity requires the check to precede the mutation. Once the field has changed, returning false only reports the problem; it does not undo it.

**Plausible wrong approach.** Patching it with `Balance -= amount; if (Balance < 0) { Balance += amount; return false; }` restores the value but briefly publishes -1. Any exception or concurrent reader between the two statements sees the broken invariant.

**How to verify.** Run Example A against the buggy method: `!wallet.TrySpend(7) && wallet.Balance == 6` throws because the balance is -1. With the check moved first, it passes.

### Task 5: Boundary evidence

Test exactly the available amount, zero and a negative request.

**Written answer.** With a wallet of 5, check `TrySpend(5)` returns true and leaves 0, `TrySpend(0)` returns true and leaves the balance unchanged, and `TrySpend(-1)` throws `ArgumentOutOfRangeException` with the balance unchanged.

**Why it is correct.** `amount > Balance` is false when they are equal, so spending exactly the available amount is accepted. Zero passes both guards as a no-op, and a negative value is caught by the first guard before any change.

**Plausible wrong approach.** Writing the affordability test as `amount >= Balance` rejects spending the full balance, so `TrySpend(5)` on a balance of 5 returns false. A test that only used 3 and 7 would never notice.

**How to verify.** Run the three cases in order on fresh wallets and check each return value and the final `Balance`. Then temporarily change `>` to `>=` and confirm the exact-amount check throws.

### Task 6: Transfer and justify

Explain whether a shared wallet needs synchronization when several tasks may spend concurrently.

**Written answer.** Yes. `TrySpend` reads `Balance`, compares and then writes, so two tasks can both read 10, both find 7 affordable, and both subtract, leaving -4. Protect the read, compare and write with one `lock` on a private object.

**Why it is correct.** The invariant holds only if the check and the mutation happen as one step. A lock serializes callers so the second task sees the balance after the first spend. The cost is contention; a single-threaded wallet does not need it.

**Plausible wrong approach.** Marking `Balance` as `volatile` or reading it with `Interlocked.Read` makes each individual read fresh but does not join the read and the write, so the same double spend still occurs.

**How to verify.** Start 100 tasks that each call `TrySpend(1)` on a wallet of 50 and count the true results. With the lock, exactly 50 succeed and the balance is 0; without it, repeated runs can produce a negative balance.

## Mechanism and diagnostic reasoning

A class can protect a state transition by admitting changes only through reviewed operations. A constructor establishes the initial invariant; methods preserve it. Private setters are useful only when the public operations actually enforce the domain rule. A property named Balance that any caller can replace with a negative number has no meaningful protection.

Model expected rejection distinctly from programming defects. A withdrawal larger than the available balance can be a normal false result. A negative withdrawal is malformed input and may merit an argument exception. State should remain unchanged on rejected operations. This failure atomicity is often more important than a compact implementation.

A constructor has the class name and no return type. `private set` permits mutation inside the class. `sealed` prevents inheritance when extension is not part of the design. Guard clauses reject invalid inputs before state changes.

Private fields alone do not establish a correct contract. A partially mutated object after failure can poison later operations. This class is intentionally single-threaded; encapsulation does not itself provide synchronization.

## Review before continuing

Run the reference and confirm it prints `csharp-013: passed`, then rerun the guide's counterexample.

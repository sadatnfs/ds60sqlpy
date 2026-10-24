import { strict as assert } from "node:assert";

function validCents(value: number): void {
  if (!Number.isSafeInteger(value) || value < 0)
    throw new RangeError("nonnegative safe integer cents required");
}
class Wallet {
  #balance: number;
  constructor(initial: number) {
    validCents(initial);
    this.#balance = initial;
  }
  get cents(): number {
    return this.#balance;
  }
  deposit(amount: number): void {
    validCents(amount);
    const next = this.#balance + amount;
    validCents(next);
    this.#balance = next;
  }
  withdraw(amount: number): void {
    validCents(amount);
    if (amount > this.#balance) throw new RangeError("insufficient balance");
    this.#balance -= amount;
  }
}
interface Clock {
  now(): Date;
}
class ReceiptService {
  constructor(private readonly clock: Clock) {}
  create(id: string): { id: string; createdAt: string } {
    if (id === "") throw new TypeError("id required");
    return { id, createdAt: this.clock.now().toISOString() };
  }
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Maintain balance through methods
  {
    const wallet = new Wallet(100);
    wallet.deposit(50);
    wallet.withdraw(30);
    assert.equal(wallet.cents, 120);
    assert.equal(Object.hasOwn(wallet, "balance"), false);
    assert.deepEqual(Object.keys(wallet), []);
  }

  // Exercise 2: Inject a deterministic clock
  {
    const service = new ReceiptService({ now: () => new Date("2026-01-01T00:00:00.000Z") });
    assert.deepEqual(service.create("A"), { id: "A", createdAt: "2026-01-01T00:00:00.000Z" });
  }

  // Exercise 3: Reject invalid transitions without mutation
  {
    const wallet = new Wallet(100);
    assert.throws(() => wallet.deposit(-1), RangeError);
    assert.throws(() => wallet.withdraw(101), RangeError);
    assert.equal(wallet.cents, 100);
  }

  // Exercise 4: Guard derived overflow
  {
    const wallet = new Wallet(Number.MAX_SAFE_INTEGER);
    assert.throws(() => wallet.deposit(1), RangeError);
    assert.equal(wallet.cents, Number.MAX_SAFE_INTEGER);
  }

  // Exercise 5: Reject an incompatible collaborator
  {
    function negativeTypeCheck(): void {
      // @ts-expect-error Clock.now must return Date.
      new ReceiptService({ now: () => "today" });
    }
    void negativeTypeCheck;
    assert.equal(
      new ReceiptService({ now: () => new Date(0) }).create("B").createdAt,
      "1970-01-01T00:00:00.000Z",
    );
  }

  // Exercise 6: Distinguish private storage from a lookalike property
  {
    const wallet = new Wallet(2);
    Object.assign(wallet, { balance: 999 });
    assert.equal(Reflect.get(wallet, "balance"), 999);
    assert.equal(wallet.cents, 2);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

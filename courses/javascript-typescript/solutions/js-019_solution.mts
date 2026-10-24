import { strict as assert } from "node:assert";

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Annotate a numeric function
  {
    function add(left: number, right: number): number {
      return left + right;
    }
    const result = add(2, 3);
    assert.equal(result, 5);
    assert.equal(typeof result, "number");
    function negativeTypeCheck(): void {
      // @ts-expect-error A string is not a numeric argument.
      add("2", 3);
    }
    void negativeTypeCheck;
  }

  // Exercise 2: Show that an assertion does not convert data
  {
    const external: unknown = "wrong";
    const claimed = external as number;
    assert.equal(typeof claimed, "string");
    assert.equal(String(claimed), "wrong");
  }

  // Exercise 3: Compare literal preservation and widening
  {
    const fixed = "ready";
    let mutable = "ready";
    mutable = "done";
    function acceptReady(value: "ready"): string {
      return value;
    }
    assert.equal(acceptReady(fixed), "ready");
    assert.equal(mutable, "done");
    function negativeTypeCheck(): void {
      // @ts-expect-error mutable is string, not the literal type ready.
      acceptReady(mutable);
    }
    void negativeTypeCheck;
  }

  // Exercise 4: Handle null explicitly under strict checking
  {
    function lengthOrZero(value: string | null): number {
      return value === null ? 0 : value.length;
    }
    assert.equal(lengthOrZero("abc"), 3);
    assert.equal(lengthOrZero(null), 0);
    function negativeTypeCheck(value: string | null): void {
      // @ts-expect-error value may be null before a guard.
      void value.length;
    }
    void negativeTypeCheck;
  }

  // Exercise 5: Observe type erasure through object keys
  {
    type Item = { id: string; count: number };
    const item: Item = { id: "A", count: 2 };
    assert.deepEqual(Object.keys(item), ["id", "count"]);
    assert.equal("Item" in item, false);
  }

  // Exercise 6: Narrow unknown before numeric use
  {
    function doubleFinite(value: unknown): number {
      if (typeof value !== "number" || !Number.isFinite(value))
        throw new TypeError("finite number required");
      return value * 2;
    }
    assert.equal(doubleFinite(12), 24);
    assert.throws(() => doubleFinite("12"), TypeError);
    assert.throws(() => doubleFinite(Infinity), TypeError);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

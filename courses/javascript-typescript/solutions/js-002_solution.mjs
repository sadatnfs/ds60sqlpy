import { strict as assert } from "node:assert";

function parseFinite(text) {
  if (typeof text !== "string" || text.trim() === "")
    throw new TypeError("nonblank numeric text required");
  const value = Number(text);
  if (!Number.isFinite(value)) throw new TypeError("finite number required");
  return value;
}

export async function verify() {
  // Exercise 1: Trace plus versus numeric conversion
  {
    assert.equal(2 + 3, 5);
    assert.equal(2 + "3", "23");
    assert.equal(Number("3") + 2, 5);
  }

  // Exercise 2: Inspect absence and NaN
  {
    assert.equal(typeof null, "object");
    assert.equal(typeof undefined, "undefined");
    assert.equal(Number.isNaN(NaN), true);
    assert.equal(Number.isNaN("not a number"), false);
  }

  // Exercise 3: Compare equality contracts
  {
    assert.equal(NaN === NaN, false);
    assert.equal(Object.is(NaN, NaN), true);
    assert.equal(0 === -0, true);
    assert.equal(Object.is(0, -0), false);
  }

  // Exercise 4: Expose floating-point approximation
  {
    const value = 0.1 + 0.2;
    assert.notEqual(value, 0.3);
    assert.ok(Math.abs(value - 0.3) < 1e-15);
  }

  // Exercise 5: Protect integer identity
  {
    const max = Number.MAX_SAFE_INTEGER;
    assert.equal(max + 1, max + 2);
    const exact = BigInt(max);
    assert.notEqual(exact + 1n, exact + 2n);
  }

  // Exercise 6: Reject ambiguous numeric input
  {
    assert.equal(parseFinite("12"), 12);
    assert.throws(() => parseFinite(" "), TypeError);
    assert.throws(() => parseFinite("Infinity"), TypeError);
    assert.throws(() => 1n + 1, TypeError);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

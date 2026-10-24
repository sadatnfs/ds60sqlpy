import { strict as assert } from "node:assert";

function identifier(value) {
  if (typeof value !== "string" || value.length > 20 || !/^[A-Za-z_][A-Za-z0-9_]*$/u.test(value))
    throw new TypeError("bounded ASCII identifier required");
  return value;
}

export async function verify() {
  // Exercise 1: Count code units and codepoints
  {
    const text = "A🙂";
    assert.equal(text.length, 3);
    assert.equal([...text].length, 2);
    assert.equal(text.codePointAt(1), 0x1f642);
  }

  // Exercise 2: Compare canonical spellings
  {
    const composed = "é";
    const decomposed = "é";
    assert.notEqual(composed, decomposed);
    assert.equal(decomposed.normalize("NFC"), composed);
  }

  // Exercise 3: Match a literal regex fragment
  {
    const literal = "a.b+";
    const pattern = new RegExp(`^${RegExp.escape(literal)}$`, "u");
    assert.equal(pattern.test("a.b+"), true);
    assert.equal(pattern.test("axbb"), false);
  }

  // Exercise 4: Observe global regex cursor state
  {
    const pattern = /a/g;
    assert.equal(pattern.test("aa"), true);
    assert.equal(pattern.lastIndex, 1);
    assert.equal(pattern.test("aa"), true);
    assert.equal(pattern.lastIndex, 2);
    assert.equal(pattern.test("aa"), false);
    assert.equal(pattern.lastIndex, 0);
  }

  // Exercise 5: Use Unicode-aware dot matching
  {
    assert.equal(/^.$/.test("🙂"), false);
    assert.equal(/^.$/u.test("🙂"), true);
  }

  // Exercise 6: Bound a text-validation input
  {
    assert.equal(identifier("item_1"), "item_1");
    assert.throws(() => identifier("a".repeat(21)), TypeError);
    assert.throws(() => identifier("two words"), TypeError);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

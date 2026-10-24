import { strict as assert } from "node:assert";

export async function verify() {
  // Exercise 1: Distinguish own and inherited properties
  {
    const parent = { kind: "record" };
    const child = Object.create(parent);
    child.name = "sample";
    assert.equal("kind" in child, true);
    assert.equal(Object.hasOwn(child, "kind"), false);
    assert.equal(Object.hasOwn(child, "name"), true);
  }

  // Exercise 2: Copy only own enumerable fields
  {
    const child = Object.create({ kind: "record" });
    child.name = "sample";
    const copy = { ...child };
    assert.deepEqual(Object.keys(copy), ["name"]);
    assert.equal(copy.kind, undefined);
  }

  // Exercise 3: Use destructuring defaults carefully
  {
    const { count: absent = 0 } = {};
    const { count: explicit = 0 } = { count: null };
    assert.equal(absent, 0);
    assert.equal(explicit, null);
  }

  // Exercise 4: Use a null-prototype dictionary for arbitrary keys
  {
    const dictionary = Object.create(null);
    dictionary["__proto__"] = "literal data";
    assert.equal(dictionary["__proto__"], "literal data");
    assert.equal(Object.getPrototypeOf(dictionary), null);
    assert.equal(Object.hasOwn(dictionary, "__proto__"), true);
  }

  // Exercise 5: Expose shallow freeze
  {
    const value = Object.freeze({ nested: { count: 1 } });
    assert.throws(() => {
      value.nested = {};
    }, TypeError);
    value.nested.count = 2;
    assert.equal(value.nested.count, 2);
  }

  // Exercise 6: Observe a getter side effect
  {
    let calls = 0;
    const value = {
      get next() {
        calls += 1;
        return calls;
      },
    };
    assert.equal(value.next, 1);
    assert.equal(value.next, 2);
    assert.equal(calls, 2);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

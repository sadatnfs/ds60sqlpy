import { strict as assert } from "node:assert";

export async function verify() {
  // Exercise 1: Keep equal-looking object keys distinct
  {
    const first = { id: 1 };
    const second = { id: 1 };
    const map = new Map([
      [first, "a"],
      [second, "b"],
    ]);
    assert.equal(map.size, 2);
    assert.equal(map.get(first), "a");
    assert.equal(map.get(second), "b");
  }

  // Exercise 2: Inspect Set equality
  {
    const values = new Set([NaN, NaN, 0, -0]);
    assert.equal(values.size, 2);
    assert.equal(values.has(NaN), true);
    assert.equal(values.has(-0), true);
  }

  // Exercise 3: Count repeated events
  {
    const counts = new Map();
    for (const value of ["red", "blue", "red"]) counts.set(value, (counts.get(value) ?? 0) + 1);
    assert.deepEqual(
      [...counts],
      [
        ["red", 2],
        ["blue", 1],
      ],
    );
  }

  // Exercise 4: Distinguish a stored zero from absence
  {
    const map = new Map([["a", 0]]);
    assert.equal(map.has("a"), true);
    assert.equal(map.get("a"), 0);
    assert.equal(map.has("b"), false);
    assert.equal(map.get("b"), undefined);
  }

  // Exercise 5: Trace insertion order updates
  {
    const map = new Map([
      ["a", 1],
      ["b", 2],
    ]);
    map.set("a", 3);
    assert.deepEqual([...map.keys()], ["a", "b"]);
    map.delete("a");
    map.set("a", 4);
    assert.deepEqual([...map.keys()], ["b", "a"]);
  }

  // Exercise 6: Deduplicate while preserving first occurrence
  {
    const unique = [...new Set(["b", "a", "b", "c", "a"])];
    assert.deepEqual(unique, ["b", "a", "c"]);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

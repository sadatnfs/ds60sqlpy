import { strict as assert } from "node:assert";

export async function verify() {
  // Exercise 1: Map and filter without changing input
  {
    const original = [1, 2, 3, 4];
    const result = original.map((value) => value * 2).filter((value) => value > 4);
    assert.deepEqual(result, [6, 8]);
    assert.deepEqual(original, [1, 2, 3, 4]);
  }

  // Exercise 2: Supply a reduction identity
  {
    assert.equal(
      [].reduce((sum, value) => sum + value, 0),
      0,
    );
    assert.equal(
      [1, 2, 3].reduce((sum, value) => sum + value, 0),
      6,
    );
  }

  // Exercise 3: Expose default sort coercion
  {
    assert.deepEqual([10, 2, 1].sort(), [1, 10, 2]);
    assert.deepEqual(
      [10, 2, 1].sort((a, b) => a - b),
      [1, 2, 10],
    );
  }

  // Exercise 4: Preserve an array while sorting
  {
    const original = [3, 1, 2];
    const sorted = original.toSorted((a, b) => a - b);
    assert.deepEqual(sorted, [1, 2, 3]);
    assert.deepEqual(original, [3, 1, 2]);
  }

  // Exercise 5: Expose a shallow copy alias
  {
    const original = [{ value: 1 }];
    const copy = [...original];
    copy[0].value = 9;
    assert.equal(original[0].value, 9);
    assert.notEqual(copy, original);
  }

  // Exercise 6: Copy records for a specific edit
  {
    const original = [{ value: 1 }];
    const copy = original.map((row) => ({ ...row }));
    copy[0].value = 9;
    assert.equal(original[0].value, 1);
    assert.equal(copy[0].value, 9);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

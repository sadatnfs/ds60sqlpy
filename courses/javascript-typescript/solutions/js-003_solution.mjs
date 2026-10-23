import { strict as assert } from 'node:assert';



export async function verify() {
  // Exercise 1: Compare false and truthy containers
  {
    assert.deepEqual([Boolean(0), Boolean(''), Boolean([]), Boolean({})], [false, false, true, true]);
  }

  // Exercise 2: Preserve a valid zero with nullish fallback
  {
    assert.equal(0 || 10, 10);
    assert.equal(0 ?? 10, 0);
    assert.equal(null ?? 10, 10);
  }

  // Exercise 3: Trace a prefix sum
  {
    let sum = 0;
    const prefixes = [];
    for (const value of [2, 4, 6]) { sum += value; prefixes.push(sum); }
    assert.deepEqual(prefixes, [2, 6, 12]);
  }

  // Exercise 4: Handle an empty collection
  {
    let sum = 0;
    let iterations = 0;
    for (const value of []) { sum += value; iterations += 1; }
    assert.equal(sum, 0);
    assert.equal(iterations, 0);
  }

  // Exercise 5: Stop at the first match
  {
    const values = [3, 8, 8];
    let found = -1;
    for (let index = 0; index < values.length; index += 1) {
      if (values[index] === 8) { found = index; break; }
    }
    assert.equal(found, 1);
  }

  // Exercise 6: Make a wrong boundary observable
  {
    const values = [7];
    const observed = [];
    for (let index = 0; index <= values.length; index += 1) observed.push(values[index]);
    assert.deepEqual(observed, [7, undefined]);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

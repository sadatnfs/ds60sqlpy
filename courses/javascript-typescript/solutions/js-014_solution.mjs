import { strict as assert } from "node:assert";

function lowerBound(values, target, trace = []) {
  let low = 0;
  let high = values.length;
  while (low < high) {
    const middle = low + Math.floor((high - low) / 2);
    trace.push([low, high, middle]);
    if (values[middle] < target) low = middle + 1;
    else high = middle;
  }
  return low;
}
function uniqueIndex(rows) {
  const index = new Map();
  for (const row of rows) {
    if (index.has(row.id)) throw new Error(`duplicate id ${row.id}`);
    index.set(row.id, row);
  }
  return index;
}
class MinHeap {
  values = [];
  push(value) {
    if (!Number.isFinite(value)) throw new TypeError("finite value required");
    const values = this.values;
    values.push(value);
    let index = values.length - 1;
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (values[parent] <= values[index]) break;
      [values[parent], values[index]] = [values[index], values[parent]];
      index = parent;
    }
  }
  pop() {
    const values = this.values;
    if (values.length === 0) return undefined;
    const minimum = values[0];
    const last = values.pop();
    if (values.length === 0) return minimum;
    values[0] = last;
    let index = 0;
    while (2 * index + 1 < values.length) {
      let child = 2 * index + 1;
      if (child + 1 < values.length && values[child + 1] < values[child]) child += 1;
      if (values[index] <= values[child]) break;
      [values[index], values[child]] = [values[child], values[index]];
      index = child;
    }
    return minimum;
  }
}

export async function verify() {
  // Exercise 1: Trace lower bound with duplicates
  {
    const trace = [];
    assert.equal(lowerBound([1, 4, 4, 8], 4, trace), 1);
    assert.deepEqual(trace, [
      [0, 4, 2],
      [0, 2, 1],
      [0, 1, 0],
    ]);
  }

  // Exercise 2: Use a heap for repeated minimum extraction
  {
    const heap = new MinHeap();
    for (const value of [5, 1, 3, 1]) heap.push(value);
    assert.deepEqual([heap.pop(), heap.pop(), heap.pop(), heap.pop()], [1, 1, 3, 5]);
    assert.equal(heap.pop(), undefined);
  }

  // Exercise 3: Cover empty and outside search boundaries
  {
    assert.equal(lowerBound([], 4), 0);
    assert.equal(lowerBound([2, 4, 6], 1), 0);
    assert.equal(lowerBound([2, 4, 6], 9), 3);
  }

  // Exercise 4: Measure comparisons without a timing claim
  {
    const values = Array.from({ length: 1024 }, (_, index) => index * 2);
    const trace = [];
    assert.equal(lowerBound(values, 1001, trace), 501);
    assert.ok(trace.length <= 11);
    assert.equal(values.includes(1001), false);
  }

  // Exercise 5: Reject duplicate index keys
  {
    const index = uniqueIndex([
      { id: "A", value: 7 },
      { id: "B", value: 9 },
    ]);
    assert.equal(index.get("A").value, 7);
    assert.throws(() => uniqueIndex([{ id: "A" }, { id: "A" }]), /duplicate/u);
  }

  // Exercise 6: Check the heap invariant after every update
  {
    const heap = new MinHeap();
    for (const value of [6, 5, 4, 3, 2, 1]) {
      heap.push(value);
      for (let index = 1; index < heap.values.length; index += 1) {
        assert.ok(heap.values[Math.floor((index - 1) / 2)] <= heap.values[index]);
      }
    }
    assert.throws(() => heap.push(NaN), TypeError);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

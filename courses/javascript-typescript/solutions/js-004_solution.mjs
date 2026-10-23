import { strict as assert } from 'node:assert';

function counter(step = 1) {
  if (!Number.isInteger(step) || step <= 0) throw new TypeError('positive integer step required');
  let value = 0;
  return () => { value += step; return value; };
}

export async function verify() {
  // Exercise 1: Call a pure function
  {
    function add(left, right) { return left + right; }
    assert.equal(add(2, 3), 5);
    assert.equal(add(-1, 1), 0);
  }

  // Exercise 2: Build independent closures
  {
    const first = counter();
    const second = counter();
    assert.equal(first(), 1);
    assert.equal(first(), 2);
    assert.equal(second(), 1);
  }

  // Exercise 3: Compare let and var loop capture
  {
    const block = [];
    for (let index = 0; index < 3; index += 1) block.push(() => index);
    const shared = [];
    for (var index = 0; index < 3; index += 1) shared.push(() => index);
    assert.deepEqual(block.map(fn => fn()), [0, 1, 2]);
    assert.deepEqual(shared.map(fn => fn()), [3, 3, 3]);
  }

  // Exercise 4: Distinguish undefined from null defaults
  {
    function label(value = 'guest') { return value; }
    assert.equal(label(), 'guest');
    assert.equal(label(undefined), 'guest');
    assert.equal(label(null), null);
  }

  // Exercise 5: Observe an ordinary receiver
  {
    const item = { value: 4, read() { return this.value; } };
    assert.equal(item.read(), 4);
    assert.equal(item.read.call({ value: 9 }), 9);
  }

  // Exercise 6: Reject an invalid factory configuration
  {
    assert.throws(() => counter(0), TypeError);
    assert.throws(() => counter(1.5), TypeError);
    const next = counter(2);
    assert.deepEqual([next(), next()], [2, 4]);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

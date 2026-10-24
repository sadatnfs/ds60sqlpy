import { strict as assert } from "node:assert";

function* range(length) {
  if (!Number.isInteger(length) || length < 0 || length > 1000)
    throw new RangeError("length must be an integer from 0 to 1000");
  for (let value = 0; value < length; value += 1) yield value;
}

export async function verify() {
  // Exercise 1: Trace lazy execution
  {
    const trace = [];
    function* values() {
      trace.push("started");
      yield 2;
      trace.push("continued");
      yield 4;
    }
    const cursor = values();
    assert.deepEqual(trace, []);
    assert.deepEqual(cursor.next(), { value: 2, done: false });
    assert.deepEqual(trace, ["started"]);
    cursor.return();
  }

  // Exercise 2: Close on an early break
  {
    const trace = [];
    function* rows() {
      try {
        trace.push("opened");
        yield 1;
        yield 2;
      } finally {
        trace.push("closed");
      }
    }
    for (const value of rows()) {
      trace.push(value);
      break;
    }
    assert.deepEqual(trace, ["opened", 1, "closed"]);
  }

  // Exercise 3: Distinguish a cursor from a fresh iterable
  {
    const cursor = range(3);
    assert.deepEqual([...cursor], [0, 1, 2]);
    assert.deepEqual([...cursor], []);
    assert.deepEqual([...range(3)], [0, 1, 2]);
  }

  // Exercise 4: Inspect the final return value
  {
    function* sample() {
      yield 1;
      return 9;
    }
    const cursor = sample();
    assert.deepEqual(cursor.next(), { value: 1, done: false });
    assert.deepEqual(cursor.next(), { value: 9, done: true });
    assert.deepEqual([...sample()], [1]);
  }

  // Exercise 5: Send a value into a suspended generator
  {
    function* conversation() {
      const answer = yield "request";
      yield answer * 2;
    }
    const cursor = conversation();
    assert.equal(cursor.next().value, "request");
    assert.equal(cursor.next(4).value, 8);
    cursor.return();
  }

  // Exercise 6: Bound the range and validate configuration
  {
    assert.deepEqual([...range(0)], []);
    assert.throws(() => [...range(-1)], RangeError);
    assert.throws(() => [...range(1.5)], RangeError);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

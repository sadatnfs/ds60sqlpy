import { strict as assert } from "node:assert";
import { setTimeout as delay } from "node:timers/promises";

export async function verify() {
  // Exercise 1: Trace executor and reaction ordering
  {
    const trace = [];
    const pending = new Promise((resolve) => {
      trace.push("executor");
      resolve(3);
    });
    const observed = pending.then((value) => {
      trace.push("reaction");
      return value;
    });
    trace.push("sync");
    assert.deepEqual(trace, ["executor", "sync"]);
    assert.equal(await observed, 3);
    assert.deepEqual(trace, ["executor", "sync", "reaction"]);
  }

  // Exercise 2: Compose values and rejection recovery
  {
    const result = await Promise.resolve(4)
      .then((value) => value * 2)
      .then((value) => {
        throw new Error(`bad value ${value}`);
      })
      .catch((error) => error.message);
    assert.equal(result, "bad value 8");
  }

  // Exercise 3: Preserve input order in Promise.all
  {
    let resolveFirst;
    let resolveSecond;
    const first = new Promise((resolve) => {
      resolveFirst = resolve;
    });
    const second = new Promise((resolve) => {
      resolveSecond = resolve;
    });
    const result = Promise.all([first, second]);
    resolveSecond("second");
    resolveFirst("first");
    assert.deepEqual(await result, ["first", "second"]);
  }

  // Exercise 4: Inspect every outcome with allSettled
  {
    const error = new Error("offline");
    const outcomes = await Promise.allSettled([Promise.resolve(2), Promise.reject(error)]);
    assert.deepEqual(outcomes[0], { status: "fulfilled", value: 2 });
    assert.equal(outcomes[1].status, "rejected");
    assert.equal(outcomes[1].reason, error);
  }

  // Exercise 5: Demonstrate that race does not cancel losers
  {
    let finish;
    const trace = [];
    const slow = new Promise((resolve) => {
      finish = resolve;
    }).then((value) => {
      trace.push(value);
      return value;
    });
    assert.equal(await Promise.race([Promise.resolve("fast"), slow]), "fast");
    finish("late");
    assert.equal(await slow, "late");
    assert.deepEqual(trace, ["late"]);
  }

  // Exercise 6: Observe FIFO microtasks before an awaited timer
  {
    const trace = [];
    Promise.resolve().then(() => trace.push("promise"));
    queueMicrotask(() => trace.push("microtask"));
    trace.push("sync");
    await delay(1);
    trace.push("timer");
    assert.deepEqual(trace, ["sync", "promise", "microtask", "timer"]);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

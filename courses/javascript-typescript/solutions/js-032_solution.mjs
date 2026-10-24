import { strict as assert } from "node:assert";
import { Readable, Transform, Writable } from "node:stream";
import { pipeline, finished } from "node:stream/promises";
import { once } from "node:events";
import { setTimeout as delay } from "node:timers/promises";

export async function verify() {
  // Exercise 1: Run an actual transform pipeline
  {
    const output = [];
    const upper = new Transform({
      transform(chunk, encoding, callback) {
        callback(null, chunk.toString("utf8").toUpperCase());
      },
    });
    const sink = new Writable({
      write(chunk, encoding, callback) {
        output.push(chunk.toString());
        callback();
      },
    });
    await pipeline(Readable.from(["ab", "cd"]), upper, sink);
    assert.equal(output.join(""), "ABCD");
    assert.equal(sink.writableFinished, true);
  }

  // Exercise 2: Observe false write and drain without guessing timing
  {
    let release;
    const sink = new Writable({
      highWaterMark: 2,
      write(chunk, encoding, callback) {
        release = callback;
      },
    });
    assert.equal(sink.write(Buffer.from("ab")), false);
    assert.equal(sink.writableNeedDrain, true);
    const drained = once(sink, "drain");
    release();
    await drained;
    sink.end();
    await finished(sink);
  }

  // Exercise 3: Propagate a producer failure and destroy the sink
  {
    async function* source() {
      yield "first";
      throw new Error("source failed");
    }
    const sink = new Writable({
      write(chunk, encoding, callback) {
        callback();
      },
    });
    await assert.rejects(pipeline(Readable.from(source()), sink), /source failed/u);
    assert.equal(sink.destroyed, true);
  }

  // Exercise 4: Reject an invalid object in a transform
  {
    const checked = new Transform({
      objectMode: true,
      transform(value, encoding, callback) {
        if (value < 0) callback(new RangeError("negative item"));
        else callback(null, value * 2);
      },
    });
    const sink = new Writable({
      objectMode: true,
      write(value, encoding, callback) {
        callback();
      },
    });
    await assert.rejects(pipeline(Readable.from([1, -1]), checked, sink), RangeError);
  }

  // Exercise 5: Measure an object-mode threshold in objects
  {
    let release;
    const sink = new Writable({
      objectMode: true,
      highWaterMark: 1,
      write(value, encoding, callback) {
        release = callback;
      },
    });
    assert.equal(sink.write({ payload: "x".repeat(1000) }), false);
    assert.equal(sink.writableLength, 1);
    const drained = once(sink, "drain");
    release();
    await drained;
    sink.end();
    await finished(sink);
  }

  // Exercise 6: Abort a generator and its awaited timer
  {
    const controller = new AbortController();
    let announce;
    const ready = new Promise((resolve) => {
      announce = resolve;
    });
    let closed = false;
    async function* source() {
      try {
        announce();
        await delay(1000, undefined, { signal: controller.signal });
        yield "late";
      } finally {
        closed = true;
      }
    }
    const sink = new Writable({
      write(chunk, encoding, callback) {
        callback();
      },
    });
    const pending = pipeline(Readable.from(source()), sink, { signal: controller.signal });
    await ready;
    controller.abort();
    await assert.rejects(pending, (error) => error.name === "AbortError");
    assert.equal(closed, true);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

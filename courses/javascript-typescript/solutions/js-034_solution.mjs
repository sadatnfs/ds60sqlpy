import { strict as assert } from 'node:assert';
import { performance, monitorEventLoopDelay } from 'node:perf_hooks';
import { setTimeout as delay } from 'node:timers/promises';

function sumTo(length) {
  let total = 0;
  for (let value = 1; value <= length; value += 1) total += value;
  return total;
}

export async function verify() {
  // Exercise 1: Measure only a checked computation
  {
    const start = performance.now();
    const result = sumTo(10000);
    const elapsed = performance.now() - start;
    assert.equal(result, 50005000);
    assert.ok(Number.isFinite(elapsed) && elapsed >= 0);
    console.log(JSON.stringify({ operation: 'sumTo10000', elapsedMs: elapsed }));
  }

  // Exercise 2: Preserve repeated samples and summarize them
  {
    const samples = [];
    for (let trial = 0; trial < 5; trial += 1) {
      const start = performance.now();
      assert.equal(sumTo(1000), 500500);
      samples.push(performance.now() - start);
    }
    const sorted = [...samples].sort((a, b) => a - b);
    const median = sorted[2];
    assert.equal(samples.length, 5);
    assert.ok(samples.every(value => Number.isFinite(value) && value >= 0));
    assert.ok(median >= sorted[0] && median <= sorted[4]);
    console.log(JSON.stringify({ samplesMs: samples, medianMs: median }));
  }

  // Exercise 3: Release owned references without claiming immediate RSS change
  {
    const cache = new Map();
    for (let index = 0; index < 100; index += 1) cache.set(index, { payload: 'x'.repeat(100) });
    assert.equal(cache.size, 100);
    const before = process.memoryUsage();
    cache.clear();
    assert.equal(cache.size, 0);
    const after = process.memoryUsage();
    assert.ok(before.heapUsed > 0 && after.rss > 0);
    console.log(JSON.stringify({ before, after, retainedEntries: cache.size }));
  }

  // Exercise 4: Use and clear only owned performance entries
  {
    const prefix = 'course-js034-owned';
    try {
      performance.mark(prefix + '-start');
      assert.equal(sumTo(10), 55);
      performance.mark(prefix + '-end');
      performance.measure(prefix, prefix + '-start', prefix + '-end');
      const entries = performance.getEntriesByName(prefix, 'measure');
      assert.equal(entries.length, 1);
      assert.ok(entries[0].duration >= 0);
    } finally {
      performance.clearMarks(prefix + '-start');
      performance.clearMarks(prefix + '-end');
      performance.clearMeasures(prefix);
    }
    assert.equal(performance.getEntriesByName(prefix).length, 0);
  }

  // Exercise 5: Inspect event-loop utilization as a bounded observation
  {
    const baseline = performance.eventLoopUtilization();
    await delay(5);
    const observed = performance.eventLoopUtilization(baseline);
    assert.ok(Number.isFinite(observed.utilization));
    assert.ok(observed.utilization >= 0 && observed.utilization <= 1);
    console.log(JSON.stringify({ eventLoop: observed }));
  }

  // Exercise 6: Enable and disable a real delay monitor
  {
    const histogram = monitorEventLoopDelay({ resolution: 10 });
    histogram.enable();
    try {
      await delay(35);
      const count = Number(histogram.count);
      assert.ok(Number.isInteger(count) && count >= 0);
      if (count > 0) assert.ok(Number.isFinite(histogram.mean));
      console.log(JSON.stringify({ samples: count, meanMs: count > 0 ? histogram.mean / 1e6 : null }));
    } finally { histogram.disable(); }
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

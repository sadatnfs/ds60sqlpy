import { strict as assert } from 'node:assert';
import { setTimeout as delay } from 'node:timers/promises';

function cancellableValue(value, signal, trace) {
  return new Promise((resolve, reject) => {
    if (signal.aborted) { reject(signal.reason); return; }
    trace.push('started');
    let timer;
    function cleanup() {
      clearTimeout(timer);
      signal.removeEventListener('abort', onAbort);
      trace.push('cleaned');
    }
    function onAbort() {
      trace.push('aborted');
      cleanup();
      reject(signal.reason);
    }
    signal.addEventListener('abort', onAbort, { once: true });
    timer = setTimeout(() => {
      trace.push('completed');
      cleanup();
      resolve(value);
    }, 1);
  });
}

export async function verify() {
  // Exercise 1: Cancel a pending timer
  {
    const controller = new AbortController();
    const reason = new Error('learner cancelled');
    const pending = delay(1000, 'unused', { signal: controller.signal });
    controller.abort(reason);
    await assert.rejects(pending, error => error.name === 'AbortError' && error.cause === reason);
  }

  // Exercise 2: Reject an already aborted request before work
  {
    const controller = new AbortController();
    const reason = new Error('already stopped');
    controller.abort(reason);
    const trace = [];
    await assert.rejects(cancellableValue(7, controller.signal, trace), error => error === reason);
    assert.deepEqual(trace, []);
  }

  // Exercise 3: Complete normally and clean up once
  {
    const controller = new AbortController();
    const trace = [];
    assert.equal(await cancellableValue(7, controller.signal, trace), 7);
    controller.abort(new Error('too late'));
    assert.deepEqual(trace, ['started', 'completed', 'cleaned']);
  }

  // Exercise 4: Cancel custom work and release its timer
  {
    const controller = new AbortController();
    const trace = [];
    const reason = new Error('stop');
    const pending = cancellableValue(7, controller.signal, trace);
    controller.abort(reason);
    await assert.rejects(pending, error => error === reason);
    assert.deepEqual(trace, ['started', 'aborted', 'cleaned']);
  }

  // Exercise 5: Keep the first abort reason
  {
    const controller = new AbortController();
    const first = new Error('first');
    controller.abort(first);
    controller.abort(new Error('second'));
    assert.equal(controller.signal.reason, first);
    assert.throws(() => controller.signal.throwIfAborted(), error => error === first);
  }

  // Exercise 6: Combine caller and deadline signals
  {
    const caller = new AbortController();
    const deadline = new AbortController();
    const combined = AbortSignal.any([caller.signal, deadline.signal]);
    const reason = new Error('deadline');
    deadline.abort(reason);
    assert.equal(combined.aborted, true);
    assert.equal(combined.reason, reason);
    assert.equal(caller.signal.aborted, false);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

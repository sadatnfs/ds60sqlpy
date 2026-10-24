import { strict as assert } from "node:assert";
import { Worker } from "node:worker_threads";

async function runWorker(source, data, transferList = []) {
  const worker = new Worker(source, {
    eval: true,
    workerData: data,
    transferList,
    resourceLimits: { maxOldGenerationSizeMb: 32 },
  });
  let timer;
  try {
    return await new Promise((resolve, reject) => {
      timer = setTimeout(() => reject(new Error("worker result timeout")), 10000);
      worker.once("message", resolve);
      worker.once("error", reject);
      worker.once("exit", (code) => reject(new Error(`worker exited without a result: ${code}`)));
    });
  } finally {
    clearTimeout(timer);
    await worker.terminate();
  }
}

export async function verify() {
  // Exercise 1: Perform bounded CPU work in a real worker
  {
    const result = await runWorker(
      `const { parentPort, workerData, threadId } = require('node:worker_threads');
    let sum = 0; for (let value = 1; value <= workerData; value += 1) sum += value;
    parentPort.postMessage({ sum, threadId });`,
      10000,
    );
    assert.equal(result.sum, 50005000);
    assert.ok(result.threadId > 0);
  }

  // Exercise 2: Transfer a buffer and observe detachment
  {
    const buffer = Uint8Array.from([1, 2, 3]).buffer;
    const result = await runWorker(
      `const { parentPort, workerData } = require('node:worker_threads');
    const bytes = new Uint8Array(workerData); bytes[0] = 9; parentPort.postMessage([...bytes]);`,
      buffer,
      [buffer],
    );
    assert.equal(buffer.byteLength, 0);
    assert.deepEqual(result, [9, 2, 3]);
  }

  // Exercise 3: Distinguish cloning from shared mutation
  {
    const original = { value: 1 };
    const result = await runWorker(
      `const { parentPort, workerData } = require('node:worker_threads');
    workerData.value = 9; parentPort.postMessage(workerData.value);`,
      original,
    );
    assert.equal(result, 9);
    assert.equal(original.value, 1);
  }

  // Exercise 4: Propagate an actual worker exception
  {
    await assert.rejects(
      runWorker(`throw new Error('worker fixture failed');`, null),
      /worker fixture failed/u,
    );
  }

  // Exercise 5: Terminate an owned worker that remains alive
  {
    const worker = new Worker(
      `const { parentPort } = require('node:worker_threads'); setInterval(() => {}, 1000); parentPort.postMessage('ready');`,
      { eval: true },
    );
    try {
      assert.equal(
        await new Promise((resolve, reject) => {
          worker.once("message", resolve);
          worker.once("error", reject);
        }),
        "ready",
      );
    } finally {
      const code = await worker.terminate();
      assert.equal(typeof code, "number");
    }
  }

  // Exercise 6: Reject data that cannot be cloned
  {
    await assert.rejects(
      runWorker(
        `const { parentPort } = require('node:worker_threads'); parentPort.postMessage('unused');`,
        { callback: () => 1 },
      ),
      (error) => error.name === "DataCloneError",
    );
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

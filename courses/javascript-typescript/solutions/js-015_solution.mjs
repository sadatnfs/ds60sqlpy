import { strict as assert } from 'node:assert';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

async function runTests(body) {
  const directory = await mkdtemp(join(tmpdir(), 'course-tests-'));
  try {
    const path = join(directory, 'fixture.test.mjs');
    await writeFile(path, "import test from 'node:test';\nimport { strict as assert } from 'node:assert';\n" + body, 'utf8');
    const result = spawnSync(process.execPath, ['--test', '--test-reporter=tap', path], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
    if (result.error) throw result.error;
    if (result.signal) throw new Error(`test process terminated by ${result.signal}`);
    return result;
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

export async function verify() {
  // Exercise 1: Run a passing pure-function test
  {
    const result = await runTests("test('addition', () => { assert.equal(2 + 3, 5); });");
    assert.equal(result.status, 0, result.stderr + result.stdout);
    assert.match(result.stdout, /# pass 1/u);
  }

  // Exercise 2: Prove a wrong result fails the runner
  {
    const result = await runTests("test('deliberate regression', () => { assert.equal(2 + 3, 6); });");
    assert.notEqual(result.status, 0);
    assert.match(result.stdout, /# fail 1/u);
    assert.match(result.stdout, /AssertionError/u);
  }

  // Exercise 3: Await an asynchronous test
  {
    const result = await runTests("test('awaited value', async () => { const value = await Promise.resolve(7); assert.equal(value, 7); });");
    assert.equal(result.status, 0, result.stderr + result.stdout);
  }

  // Exercise 4: Check rejection with rejects
  {
    const result = await runTests("test('async boundary', async () => { await assert.rejects(async () => { throw new RangeError('negative'); }, RangeError); });");
    assert.equal(result.status, 0, result.stderr + result.stdout);
  }

  // Exercise 5: Cover a table of boundary cases
  {
    const body = `for (const [name, values, expected] of [['empty', [], 0], ['one', [4], 4], ['signed', [-2, 2], 0]]) {
      test(name, () => assert.equal(values.reduce((sum, value) => sum + value, 0), expected));
    }`;
    const result = await runTests(body);
    assert.equal(result.status, 0, result.stderr + result.stdout);
    assert.match(result.stdout, /# pass 3/u);
  }

  // Exercise 6: Keep fixtures independent
  {
    const result = await runTests("test('mutate local', () => { const rows = [1]; rows.push(2); assert.deepEqual(rows, [1,2]); });\ntest('fresh local', () => { const rows = [1]; assert.deepEqual(rows, [1]); });");
    assert.equal(result.status, 0, result.stderr + result.stdout);
    assert.match(result.stdout, /# pass 2/u);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

import { strict as assert } from 'node:assert';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

async function withModules(files, use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-modules-'));
  try {
    for (const [name, source] of Object.entries(files)) await writeFile(join(directory, name), source, 'utf8');
    return await use(directory);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

export async function verify() {
  // Exercise 1: Observe a live binding
  {
    await withModules({ 'counter.mjs': 'export let count = 0; export function increment() { count += 1; }' }, async directory => {
      const module = await import(pathToFileURL(join(directory, 'counter.mjs')).href);
      assert.equal(module.count, 0);
      module.increment();
      assert.equal(module.count, 1);
    });
  }

  // Exercise 2: Resolve a relative dependency
  {
    await withModules({ 'math.mjs': 'export const twice = value => 2 * value;', 'main.mjs': "import { twice } from './math.mjs'; export const answer = twice(4);" }, async directory => {
      const module = await import(pathToFileURL(join(directory, 'main.mjs')).href);
      assert.equal(module.answer, 8);
    });
  }

  // Exercise 3: Prove cached module identity
  {
    await withModules({ 'state.mjs': 'export const state = { visits: 0 };' }, async directory => {
      const url = pathToFileURL(join(directory, 'state.mjs')).href;
      const first = await import(url);
      const second = await import(url);
      assert.equal(first, second);
      assert.equal(first.state, second.state);
    });
  }

  // Exercise 4: Inspect CommonJS interoperability
  {
    await withModules({ 'legacy.cjs': "module.exports = { label: 'legacy' };" }, async directory => {
      const module = await import(pathToFileURL(join(directory, 'legacy.cjs')).href);
      assert.equal(module.default.label, 'legacy');
    });
  }

  // Exercise 5: Reject a missing dependency
  {
    await withModules({ 'broken.mjs': "import './missing.mjs';" }, async directory => {
      await assert.rejects(import(pathToFileURL(join(directory, 'broken.mjs')).href), error => error.code === 'ERR_MODULE_NOT_FOUND');
    });
  }

  // Exercise 6: Respect namespace ownership
  {
    await withModules({ 'fixed.mjs': 'export let value = 3;' }, async directory => {
      const module = await import(pathToFileURL(join(directory, 'fixed.mjs')).href);
      assert.throws(() => { module.value = 9; }, TypeError);
      assert.equal(module.value, 3);
    });
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

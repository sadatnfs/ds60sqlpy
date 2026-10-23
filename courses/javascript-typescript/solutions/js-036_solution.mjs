import { strict as assert } from 'node:assert';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

async function withPackage(use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-package-'));
  try {
    const folder = join(directory, 'node_modules/course-fixture');
    await mkdir(folder, { recursive: true });
    await writeFile(join(folder, 'package.json'), JSON.stringify({ name: 'course-fixture', version: '1.0.0', type: 'module', engines: { node: '>=99' }, exports: { '.': './index.mjs', './math': './math.mjs' } }));
    await writeFile(join(folder, 'index.mjs'), 'export const version = 1;');
    await writeFile(join(folder, 'math.mjs'), 'export const twice = value => value * 2;');
    await writeFile(join(folder, 'private.mjs'), 'export const internal = true;');
    return await use(directory);
  } finally { await rm(directory, { recursive: true, force: true }); }
}
function runImport(directory, source) {
  const path = join(directory, 'main.mjs');
  writeFileSync(path, source);
  const result = spawnSync(process.execPath, [path], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`child terminated by ${result.signal}`);
  return result;
}
function digest(bytes) { return createHash('sha256').update(bytes).digest('hex'); }

export async function verify() {
  // Exercise 1: Import the public package entry
  {
    await withPackage(async directory => {
      const result = runImport(directory, 'import { version } from \'course-fixture\'; console.log(version);');
      assert.equal(result.status, 0, result.stderr);
      assert.equal(result.stdout.trim(), '1');
    });
  }

  // Exercise 2: Use an explicitly exported subpath
  {
    await withPackage(async directory => {
      const result = runImport(directory, 'import { twice } from \'course-fixture/math\'; console.log(twice(3));');
      assert.equal(result.status, 0, result.stderr);
      assert.equal(result.stdout.trim(), '6');
    });
  }

  // Exercise 3: Reject an undeclared private path
  {
    await withPackage(async directory => {
      const result = runImport(directory, 'import \'course-fixture/private.mjs\';');
      assert.notEqual(result.status, 0);
      assert.match(result.stderr, /ERR_PACKAGE_PATH_NOT_EXPORTED/u);
    });
  }

  // Exercise 4: Observe that engines is metadata rather than a loader gate
  {
    await withPackage(async directory => {
      const manifest = JSON.parse(await readFile(join(directory, 'node_modules/course-fixture/package.json'), 'utf8'));
      assert.equal(manifest.engines.node, '>=99');
      assert.ok(Number(process.versions.node.split('.')[0]) < 99);
      assert.equal(runImport(directory, 'import \'course-fixture\';').status, 0);
    });
  }

  // Exercise 5: Detect exact source tampering through a digest
  {
    await withPackage(async directory => {
      const path = join(directory, 'node_modules/course-fixture/index.mjs');
      const before = digest(await readFile(path));
      await writeFile(path, 'export const version = 2;');
      const after = digest(await readFile(path));
      assert.notEqual(after, before);
      assert.equal(before.length, 64);
    });
  }

  // Exercise 6: Preserve a versioned behavior contract
  {
    await withPackage(async directory => {
      const result = runImport(directory, 'import { strict as assert } from \'node:assert\'; import { twice } from \'course-fixture/math\'; assert.equal(twice(0), 0); assert.equal(twice(-2), -4);');
      assert.equal(result.status, 0, result.stderr);
    });
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

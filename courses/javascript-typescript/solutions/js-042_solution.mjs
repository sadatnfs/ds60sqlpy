import { strict as assert } from 'node:assert';
import { mkdtemp, writeFile, readFile, appendFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

const APP = String.raw`import { strict as assert } from 'node:assert';
const args = process.argv.slice(2);
if (args.length !== 1 || args[0] !== '--self-test') {
  process.stderr.write(JSON.stringify({ event: 'usage_error', message: 'Use --self-test' }) + '\n');
  process.exitCode = 2;
} else {
  assert.equal(2 + 3, 5);
  assert.equal([].reduce((sum, value) => sum + value, 0), 0);
  assert.equal(Number.isSafeInteger(Number.MAX_SAFE_INTEGER + 1), false);
  process.stdout.write(JSON.stringify({ status: 'passed', checks: 3, node: process.versions.node }) + '\n');
  process.stderr.write(JSON.stringify({ event: 'self_test_complete', checks: 3 }) + '\n');
}
`;
function hash(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
async function withBundle(use) {
  const directory = await mkdtemp(join(tmpdir(), 'course-release-'));
  try {
    await writeFile(join(directory, 'app.mjs'), APP);
    await writeFile(join(directory, 'package.json'), JSON.stringify({ name: 'course-release', version: '1.0.0', type: 'module', private: true }));
    const files = [];
    for (const path of ['app.mjs', 'package.json']) files.push({ path, sha256: hash(await readFile(join(directory, path))) });
    await writeFile(join(directory, 'manifest.json'), JSON.stringify({ version: 1, files }));
    return await use(directory);
  } finally { await rm(directory, { recursive: true, force: true }); }
}
async function verifyBundle(directory) {
  const manifest = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
  if (manifest.version !== 1 || !Array.isArray(manifest.files) || manifest.files.length !== 2) throw new Error('invalid manifest');
  const allowed = new Set(['app.mjs', 'package.json']);
  const seen = new Set();
  for (const file of manifest.files) {
    if (!allowed.has(file.path) || seen.has(file.path)) throw new Error('unapproved artifact path');
    seen.add(file.path);
    if (hash(await readFile(join(directory, file.path))) !== file.sha256) throw new Error('digest mismatch');
  }
}
function runBundle(directory, args) {
  const result = spawnSync(process.execPath, [join(directory, 'app.mjs'), ...args], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`child terminated by ${result.signal}`);
  return result;
}
function qualifyRuntime(receipt, requiredMajor) {
  if (receipt.status !== 'passed' || Number(receipt.node.split('.')[0]) !== requiredMajor) throw new Error('runtime mismatch');
  return true;
}

export async function verify() {
  // Exercise 1: Build, verify and execute a fresh bundle
  {
    await withBundle(async directory => {
      await verifyBundle(directory);
      const result = runBundle(directory, ['--self-test']);
      assert.equal(result.status, 0, result.stderr);
      const receipt = JSON.parse(result.stdout);
      assert.equal(receipt.checks, 3);
      assert.equal(receipt.status, 'passed');
      assert.equal(receipt.node, process.versions.node);
    });
  }

  // Exercise 2: Reject altered application bytes before execution
  {
    await withBundle(async directory => {
      await appendFile(join(directory, 'app.mjs'), '\n// controlled tamper fixture\n');
      await assert.rejects(verifyBundle(directory), /digest mismatch/u);
    });
  }

  // Exercise 3: Reject a manifest path outside the allowlist
  {
    await withBundle(async directory => {
      const path = join(directory, 'manifest.json');
      const manifest = JSON.parse(await readFile(path, 'utf8'));
      manifest.files[0].path = '../outside.txt';
      await writeFile(path, JSON.stringify(manifest));
      await assert.rejects(verifyBundle(directory), /unapproved artifact path/u);
    });
  }

  // Exercise 4: Preserve result and diagnostic channels on failure
  {
    await withBundle(async directory => {
      const result = runBundle(directory, ['--fixture-secret-value']);
      assert.notEqual(result.status, 0);
      assert.equal(result.stdout, '');
      assert.equal(result.stderr.includes('fixture-secret-value'), false);
      const diagnostic = JSON.parse(result.stderr.trim());
      assert.equal(diagnostic.event, 'usage_error');
    });
  }

  // Exercise 5: Derive stable content identity from unchanged files
  {
    await withBundle(async directory => {
      const bytes = await readFile(join(directory, 'app.mjs'));
      const first = hash(bytes);
      const second = hash(await readFile(join(directory, 'app.mjs')));
      assert.equal(first, second);
      const manifest = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
      assert.equal(manifest.files.find(file => file.path === 'app.mjs').sha256, first);
    });
  }

  // Exercise 6: Gate an observed runtime against explicit policy
  {
    await withBundle(async directory => {
      const receipt = JSON.parse(runBundle(directory, ['--self-test']).stdout);
      const actual = Number(process.versions.node.split('.')[0]);
      assert.equal(qualifyRuntime(receipt, actual), true);
      assert.throws(() => qualifyRuntime(receipt, actual + 1), /runtime mismatch/u);
    });
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

import { strict as assert } from "node:assert";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const CLI_SOURCE = String.raw`
async function main() {
  if (process.argv.slice(2).join(' ') !== '--sum') throw new Error('usage: main.mjs --sum');
  const chunks = [];
  let bytes = 0;
  for await (const chunk of process.stdin) {
    bytes += chunk.length;
    if (bytes > 4096) throw new Error('input limit: 4096 bytes');
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString('utf8');
  const ids = new Set();
  let rows = 0;
  let totalCents = 0;
  for (const [index, line] of text.split(/\r?\n/u).entries()) {
    if (line.trim() === '') continue;
    try {
      const row = JSON.parse(line);
      if (row === null || typeof row !== 'object' || Array.isArray(row)) throw new Error('object required');
      if (Object.keys(row).sort().join(',') !== 'id,priceCents,quantity') throw new Error('exact schema required');
      if (typeof row.id !== 'string' || row.id === '') throw new Error('id required');
      if (!Number.isSafeInteger(row.quantity) || row.quantity <= 0 || !Number.isSafeInteger(row.priceCents) || row.priceCents < 0) throw new Error('invalid integer units');
      if (ids.has(row.id)) throw new Error('duplicate id');
      const contribution = row.quantity * row.priceCents;
      if (!Number.isSafeInteger(contribution) || !Number.isSafeInteger(totalCents + contribution)) throw new Error('unsafe total');
      ids.add(row.id);
      totalCents += contribution;
      rows += 1;
    } catch (error) {
      throw new Error('line ' + (index + 1) + ': ' + error.message, { cause: error });
    }
  }
  process.stdout.write(JSON.stringify({ rows, totalCents }) + '\n');
}
main().catch(error => { process.stderr.write(error.message + '\n'); process.exitCode = 2; });
`;
async function runCli(args, input) {
  const directory = await mkdtemp(join(tmpdir(), "course-cli-"));
  try {
    const path = join(directory, "main.mjs");
    await writeFile(path, CLI_SOURCE, "utf8");
    const result = spawnSync(process.execPath, [path, ...args], {
      input,
      encoding: "utf8",
      timeout: 10000,
      maxBuffer: 1024 * 1024,
    });
    if (result.error) throw result.error;
    if (result.signal) throw new Error(`CLI terminated by ${result.signal}`);
    return result;
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}

export async function verify() {
  // Exercise 1: Aggregate valid rows through a real child process
  {
    const input = [
      { id: "A", quantity: 2, priceCents: 125 },
      { id: "B", quantity: 3, priceCents: 100 },
    ]
      .map(JSON.stringify)
      .join("\n");
    const result = await runCli(["--sum"], input);
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), { rows: 2, totalCents: 550 });
    assert.equal(result.stderr, "");
    assert.equal(result.stdout.trim().split("\n").length, 1);
  }

  // Exercise 2: Reject unknown arguments before consuming data
  {
    const result = await runCli(["--unknown"], "");
    assert.equal(result.status, 2);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /usage/u);
  }

  // Exercise 3: Report the first invalid row without a partial result
  {
    const result = await runCli(["--sum"], '{"id":"A","quantity":1,"priceCents":5}\n{broken');
    assert.equal(result.status, 2);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /line 2/u);
  }

  // Exercise 4: Reject duplicate business identifiers
  {
    const row = JSON.stringify({ id: "A", quantity: 1, priceCents: 5 });
    const result = await runCli(["--sum"], row + "\n" + row);
    assert.equal(result.status, 2);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /duplicate id/u);
  }

  // Exercise 5: Define empty input deliberately
  {
    const result = await runCli(["--sum"], "\n  \n");
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(JSON.parse(result.stdout), { rows: 0, totalCents: 0 });
  }

  // Exercise 6: Enforce an input budget before retaining all data
  {
    const result = await runCli(["--sum"], "x".repeat(4097));
    assert.equal(result.status, 2);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /input limit/u);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

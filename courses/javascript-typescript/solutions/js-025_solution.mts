import { strict as assert } from "node:assert";
import { mkdtemp, writeFile, readFile, access, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";

type ProcessResult = { status: number | null; stdout: string; stderr: string };
async function withProject(
  files: Record<string, string>,
  use: (directory: string) => Promise<void>,
): Promise<void> {
  const directory = await mkdtemp(join(tmpdir(), "course-ts-project-"));
  try {
    for (const [name, source] of Object.entries(files))
      await writeFile(join(directory, name), source, "utf8");
    await use(directory);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}
function child(args: string[]): ProcessResult {
  const result = spawnSync(process.execPath, args, {
    encoding: "utf8",
    timeout: 20000,
    maxBuffer: 1024 * 1024,
  });
  if (result.error) throw result.error;
  if (result.signal) throw new Error(`child terminated by ${result.signal}`);
  return { status: result.status, stdout: result.stdout, stderr: result.stderr };
}
function compile(directory: string): ProcessResult {
  const compiler = process.env.DS60_TSC_JS ?? "/opt/typescript/node_modules/typescript/bin/tsc";
  const typeRoots = resolve(dirname(compiler), "../..", "@types");
  return child([
    compiler,
    "--target",
    "ES2022",
    "--module",
    "NodeNext",
    "--moduleResolution",
    "NodeNext",
    "--strict",
    "--noEmitOnError",
    "--skipLibCheck",
    "--types",
    "node",
    "--typeRoots",
    typeRoots,
    "--outDir",
    join(directory, "compiled"),
    join(directory, "main.mts"),
  ]);
}
function runModule(directory: string): ProcessResult {
  return child([join(directory, "compiled", "main.mjs")]);
}
async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch (error: unknown) {
    if (error instanceof Error && "code" in error && error.code === "ENOENT") return false;
    throw error;
  }
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Compile and run a two-module project
  {
    await withProject(
      {
        "math.mts": "export const twice = (value: number): number => value * 2;",
        "main.mts": "import { twice } from './math.mjs'; console.log(twice(4));",
      },
      async (directory) => {
        const compiled = compile(directory);
        assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
        const executed = runModule(directory);
        assert.equal(executed.status, 0, executed.stderr);
        assert.equal(executed.stdout.trim(), "8");
        assert.equal(await exists(join(directory, "compiled", "math.mjs")), true);
      },
    );
  }

  // Exercise 2: Inspect type-only erasure
  {
    await withProject(
      {
        "model.mts": "export type Item = { id: string };",
        "main.mts":
          "import type { Item } from './model.mjs'; const item: Item = { id: 'A' }; console.log(item.id);",
      },
      async (directory) => {
        const compiled = compile(directory);
        assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
        const emitted = await readFile(join(directory, "compiled", "main.mjs"), "utf8");
        assert.equal(emitted.includes("./model.mjs"), false);
        assert.equal(runModule(directory).stdout.trim(), "A");
      },
    );
  }

  // Exercise 3: Reject a type mismatch without output
  {
    await withProject(
      { "main.mts": "const count: number = 'wrong'; console.log(count);" },
      async (directory) => {
        const compiled = compile(directory);
        assert.notEqual(compiled.status, 0);
        assert.match(compiled.stdout + compiled.stderr, /TS2322/u);
        assert.equal(await exists(join(directory, "compiled", "main.mjs")), false);
      },
    );
  }

  // Exercise 4: Require runtime-valid relative extensions
  {
    await withProject(
      {
        "math.mts": "export const value = 2;",
        "main.mts": "import { value } from './math'; console.log(value);",
      },
      async (directory) => {
        const compiled = compile(directory);
        assert.notEqual(compiled.status, 0);
        assert.match(compiled.stdout + compiled.stderr, /TS2835/u);
        assert.equal(await exists(join(directory, "compiled", "main.mjs")), false);
      },
    );
  }

  // Exercise 5: Observe a missing runtime artifact
  {
    await withProject(
      {
        "value.mts": "export const value = 3;",
        "main.mts": "import { value } from './value.mjs'; console.log(value);",
      },
      async (directory) => {
        const compiled = compile(directory);
        assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
        await rm(join(directory, "compiled", "value.mjs"));
        const executed = runModule(directory);
        assert.notEqual(executed.status, 0);
        assert.match(executed.stderr, /ERR_MODULE_NOT_FOUND/u);
      },
    );
  }

  // Exercise 6: Retain value imports beside erased type imports
  {
    await withProject(
      {
        "model.mts": "export type Item = { id: string }; export const prefix = 'ready';",
        "main.mts":
          "import { prefix, type Item } from './model.mjs'; const item: Item = { id: 'A' }; console.log(prefix + ':' + item.id);",
      },
      async (directory) => {
        const compiled = compile(directory);
        assert.equal(compiled.status, 0, compiled.stdout + compiled.stderr);
        const emitted = await readFile(join(directory, "compiled", "main.mjs"), "utf8");
        assert.ok(emitted.includes("./model.mjs"));
        assert.equal(runModule(directory).stdout.trim(), "ready:A");
      },
    );
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

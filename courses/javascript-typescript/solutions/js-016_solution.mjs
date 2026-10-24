import { strict as assert } from "node:assert";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { createInterface } from "node:readline";
import { tmpdir } from "node:os";
import { join } from "node:path";

async function withDirectory(use) {
  const directory = await mkdtemp(join(tmpdir(), "course-files-"));
  try {
    return await use(directory);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
}
async function readLines(path) {
  const input = createReadStream(path, { encoding: "utf8", highWaterMark: 2 });
  const lines = createInterface({ input, crlfDelay: Infinity });
  const result = [];
  try {
    for await (const line of lines) result.push(line);
  } finally {
    lines.close();
    input.destroy();
  }
  return result;
}
function fixtureName(name) {
  if (typeof name !== "string" || !/^[A-Za-z0-9_-]+\.txt$/u.test(name))
    throw new TypeError("simple .txt filename required");
  return name;
}

export async function verify() {
  // Exercise 1: Read a small UTF-8 file
  {
    await withDirectory(async (directory) => {
      const path = join(directory, "message.txt");
      const text = "A😀B\n";
      await writeFile(path, text, { encoding: "utf8", flag: "wx" });
      assert.equal(await readFile(path, "utf8"), text);
      assert.equal((await readFile(path)).length, 7);
      assert.equal(text.length, 5);
    });
  }

  // Exercise 2: Preserve characters and lines across chunks
  {
    await withDirectory(async (directory) => {
      const path = join(directory, "lines.txt");
      await writeFile(path, "A😀B\r\nsecond\n", "utf8");
      assert.deepEqual(await readLines(path), ["A😀B", "second"]);
    });
  }

  // Exercise 3: Refuse accidental overwrite
  {
    await withDirectory(async (directory) => {
      const path = join(directory, "owned.txt");
      await writeFile(path, "first", { flag: "wx" });
      await assert.rejects(
        writeFile(path, "second", { flag: "wx" }),
        (error) => error.code === "EEXIST",
      );
      assert.equal(await readFile(path, "utf8"), "first");
    });
  }

  // Exercise 4: Distinguish a missing file
  {
    await withDirectory(async (directory) => {
      await assert.rejects(
        readFile(join(directory, "missing.txt")),
        (error) => error.code === "ENOENT",
      );
    });
  }

  // Exercise 5: Restrict a learner-supplied fixture name
  {
    assert.equal(fixtureName("report.txt"), "report.txt");
    for (const name of ["../report.txt", "/tmp/report.txt", "a/b.txt", "a\\b.txt"]) {
      assert.throws(() => fixtureName(name), TypeError);
    }
  }

  // Exercise 6: Handle an empty text stream
  {
    await withDirectory(async (directory) => {
      const path = join(directory, "empty.txt");
      await writeFile(path, "");
      assert.deepEqual(await readLines(path), []);
    });
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));

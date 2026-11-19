# js-016: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A filesystem path names a resource in a host filesystem. Its interpretation is separate from a file URL and from the bytes stored in the file. Use path utilities rather than concatenating platform separators. A process working directory is mutable process state, so relative paths should have a deliberate base. This lesson owns only a newly created temporary directory and never overwrites a repository or learner file.

Text is encoded as bytes. UTF-8 characters can span multiple bytes, and a stream chunk can end in the middle of a character or a line. Splitting each raw chunk into lines independently can corrupt characters and split records. Node's stream decoder and readline interface preserve the needed partial state across chunks. We deliberately use two-byte chunks with a four-byte emoji to expose this boundary.

Reading a whole small file is straightforward. Streaming allows incremental processing, but memory still grows if the application pushes every record into a result array. A maximum byte or record policy must be enforced where data enters. The fixture has a tiny known size; its decoder and line framing are reusable mechanisms, not a claim of constant memory for arbitrary records. Filesystem errors retain codes such as ENOENT and EEXIST so callers can distinguish absence, exclusive-create conflicts and other failures.

**Encoding:** The mapping between text characters and stored bytes.

**Chunk boundary:** An arbitrary split in delivered bytes, independent of character or record boundaries.

**Exclusive creation:** Creating a new file only if it does not already exist.

**Resource lifetime:** The interval during which a file handle, stream or interface is owned.

## Reading the implementation

mkdtemp allocates a unique directory under tmpdir. writeFile with flag wx rejects an existing file instead of replacing it. readFile with utf8 decodes text; without an encoding it returns bytes. createReadStream with encoding utf8 retains incomplete character sequences between chunks. createInterface with crlfDelay:Infinity treats CRLF consistently across chunks. for await consumes lines until completion, and finally closes both the interface and stream. open returns a FileHandle; declaring it with await using closes it when its block ends by awaiting its Symbol.asyncDispose method, and a closed handle reports fd -1. Path containment based only on resolve does not defend against symlink races, so the lesson's lexical name check is scoped to files it creates itself.

## Exercise 1: Read a small UTF-8 file: change one input

Task: Copy Example A into a scratch `main.mjs` and change `const text = 'A😀B\n';` to `const text = 'A😀B\n!';`. Before running it, predict which check fails and which value it now sees; then run it and restore the original line.

The emoji occupies four UTF-8 bytes and two UTF-16 code units. Neither byte count nor JavaScript string length is a universal count of user-perceived characters. The await using declaration closes the FileHandle when its block ends, even if a read throws, so no descriptor stays open; the retained reference only proves that by reporting fd -1.

The unchanged code is the exercise block of Example A:

```javascript
await withDirectory(async (directory) => {
  const path = join(directory, 'message.txt');
  const text = 'A😀B\n';
  await writeFile(path, text, { encoding: 'utf8', flag: 'wx' });
  let owned;
  {
    await using handle = await open(path, 'r');
    owned = handle;
    assert.equal((await handle.readFile()).length, 7);
  }
  assert.equal(owned.fd, -1);
  assert.equal(await readFile(path, 'utf8'), text);
  assert.equal(text.length, 5);
});
```

**Expected:** The changed run fails with an `AssertionError` at the check `assert.equal((await handle.readFile()).length, 7)`. Restoring the original line brings back the worked observation: text round-trips; 7 UTF-8 bytes versus 5 code units; the handle reports fd -1 after its block.

**Verify:** Compare your written prediction with the reported `AssertionError`, including its actual and expected values, and name the value that made `assert.equal((await handle.readFile()).length, 7)` fail. After restoring the line, the program prints its `{"checks":1,"status":"passed"}` receipt again.

## Exercise 2: Preserve characters and lines across chunks: debug a regression

Task: A regression changed one token in Example B, so one line now reads `await writeFile(path, 'A😀B\r\nsecond\n!', 'utf8');`. Run Example B with that line, use the failing check to locate the defect and repair it without changing the check.

The stream decoder retains incomplete UTF-8 sequences, while readline retains incomplete lines. Chunk size is not a record size or a guarantee about the bytes held by every layer.

The unchanged code is the exercise block of Example B:

```javascript
await withDirectory(async (directory) => {
  const path = join(directory, 'lines.txt');
  await writeFile(path, 'A😀B\r\nsecond\n', 'utf8');
  assert.deepEqual(await readLines(path), ['A😀B', 'second']);
});
```

**Expected:** Before the repair the run fails with an `AssertionError` at the check `assert.deepEqual(await readLines(path), ['A😀B', 'second'])`; after it the line reads `await writeFile(path, 'A😀B\r\nsecond\n', 'utf8');` again and lines are A😀B and second, without a corrupt replacement character.

**Verify:** Keep the failing and the repaired runs. Explain why the changed token alters the value tested by `assert.deepEqual(await readLines(path), ['A😀B', 'second'])` for this input.

## Exercise 3: Refuse accidental overwrite

Task: Create a file exclusively twice and inspect its unchanged content.

Checking existence before writing introduces a race. Exclusive creation combines the check and creation at the filesystem operation boundary.

```javascript
await withDirectory(async (directory) => {
  const path = join(directory, 'owned.txt');
  await writeFile(path, 'first', { flag: 'wx' });
  await assert.rejects(
    writeFile(path, 'second', { flag: 'wx' }),
    (error) => error.code === 'EEXIST',
  );
  assert.equal(await readFile(path, 'utf8'), 'first');
});
```

**Expected:** second creation rejects with EEXIST; original first remains.

**Verify:** Keep a check equivalent to `assert.equal(await readFile(path, 'utf8'), 'first')`. As a control, change `await writeFile(path, 'first', { flag: 'wx' });` to `await writeFile(path, 'first!', { flag: 'wx' });`: the run must fail with an `AssertionError` at that check. Restore the line before continuing.

## Exercise 4: Distinguish a missing file

Task: Read a path known not to exist in the fresh directory.

A missing file can have an intentional application policy, but a catch-all empty result would also hide permission and I/O errors. Match the specific failure you intend to handle.

```javascript
await withDirectory(async (directory) => {
  await assert.rejects(
    readFile(join(directory, 'missing.txt')),
    (error) => error.code === 'ENOENT',
  );
});
```

**Expected:** ENOENT rejection.

**Verify:** Keep a check equivalent to `assert.rejects(readFile(join(directory, 'missing.txt')), (error) => error.code === 'ENOENT')`. As a control, change `await assert.rejects(readFile(join(directory, 'missing.txt')), error => error.code === 'ENOENT');` to `await assert.rejects(readFile(join(directory, 'missing.txt')), error => error.code !== 'ENOENT');` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 5: Restrict a learner-supplied fixture name

Task: Accept report.txt but reject traversal, separators and an absolute path.

This allowlist accepts a single simple filename, avoiding platform-dependent separator interpretation. It is deliberately narrower than a general path sanitizer and makes no symlink-security claim.

```javascript
assert.equal(fixtureName('report.txt'), 'report.txt');
for (const name of ['../report.txt', '/tmp/report.txt', 'a/b.txt', 'a\\b.txt']) {
  assert.throws(() => fixtureName(name), TypeError);
}
```

**Expected:** only report.txt is accepted.

**Verify:** Keep a check equivalent to `assert.equal(fixtureName('report.txt'), 'report.txt')`. As a control, change `assert.equal(fixtureName('report.txt'), 'report.txt');` to `assert.equal(fixtureName('report.txt'), 'report.txt!');` inside it: the run must fail with an `AssertionError`, which shows the check can fail. Restore it.

## Exercise 6: Handle an empty text stream

Task: Stream an empty file with the same decoder and line interface.

The absence of bytes means no records. Adding a fabricated empty line would change aggregation counts and confuse empty input with one empty record.

```javascript
await withDirectory(async (directory) => {
  const path = join(directory, 'empty.txt');
  await writeFile(path, '');
  assert.deepEqual(await readLines(path), []);
});
```

**Expected:** no lines.

**Verify:** Keep a check equivalent to `assert.deepEqual(await readLines(path), [])` and confirm that the reference still passes. Then name an input that would make it fail and explain which value changes.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.

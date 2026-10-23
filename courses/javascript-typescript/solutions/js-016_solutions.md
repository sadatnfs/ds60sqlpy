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

mkdtemp allocates a unique directory under tmpdir. writeFile with flag wx rejects an existing file instead of replacing it. readFile with utf8 decodes text; without an encoding it returns bytes. createReadStream with encoding utf8 retains incomplete character sequences between chunks. createInterface with crlfDelay:Infinity treats CRLF consistently across chunks. for await consumes lines until completion, and finally closes both the interface and stream. Path containment based only on resolve does not defend against symlink races, so the lesson's lexical name check is scoped to files it creates itself.

## Exercise 1: Read a small UTF-8 file

Task: Write one line containing an emoji, then compare text length and byte length.

The emoji occupies four UTF-8 bytes and two UTF-16 code units. Neither byte count nor JavaScript string length is a universal count of user-perceived characters.

```javascript
await withDirectory(async directory => {
  const path = join(directory, 'message.txt');
  const text = 'A😀B\n';
  await writeFile(path, text, { encoding: 'utf8', flag: 'wx' });
  assert.equal(await readFile(path, 'utf8'), text);
  assert.equal((await readFile(path)).length, 7);
  assert.equal(text.length, 5);
});
```

**Expected:** text round-trips; UTF-8 byte length exceeds code-unit length.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Preserve characters and lines across chunks

Task: Stream two lines with a two-byte highWaterMark and decode using readline.

The stream decoder retains incomplete UTF-8 sequences, while readline retains incomplete lines. Chunk size is not a record size or a guarantee about the bytes held by every layer.

```javascript
await withDirectory(async directory => {
  const path = join(directory, 'lines.txt');
  await writeFile(path, 'A😀B\r\nsecond\n', 'utf8');
  assert.deepEqual(await readLines(path), ['A😀B', 'second']);
});
```

**Expected:** lines are A😀B and second, without a corrupt replacement character.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Refuse accidental overwrite

Task: Create a file exclusively twice and inspect its unchanged content.

Checking existence before writing introduces a race. Exclusive creation combines the check and creation at the filesystem operation boundary.

```javascript
await withDirectory(async directory => {
  const path = join(directory, 'owned.txt');
  await writeFile(path, 'first', { flag: 'wx' });
  await assert.rejects(writeFile(path, 'second', { flag: 'wx' }), error => error.code === 'EEXIST');
  assert.equal(await readFile(path, 'utf8'), 'first');
});
```

**Expected:** second creation rejects with EEXIST; original first remains.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Distinguish a missing file

Task: Read a path known not to exist in the fresh directory.

A missing file can have an intentional application policy, but a catch-all empty result would also hide permission and I/O errors. Match the specific failure you intend to handle.

```javascript
await withDirectory(async directory => {
  await assert.rejects(readFile(join(directory, 'missing.txt')), error => error.code === 'ENOENT');
});
```

**Expected:** ENOENT rejection.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

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

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Handle an empty text stream

Task: Stream an empty file with the same decoder and line interface.

The absence of bytes means no records. Adding a fabricated empty line would change aggregation counts and confuse empty input with one empty record.

```javascript
await withDirectory(async directory => {
  const path = join(directory, 'empty.txt');
  await writeFile(path, '');
  assert.deepEqual(await readLines(path), []);
});
```

**Expected:** no lines.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.

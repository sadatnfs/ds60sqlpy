// Answer-free learner source. Save your own copy before editing.
// Exercise 1: Read a small UTF-8 file: change one input
// In a scratch copy of Example A, change `const text = 'A😀B\n';` to `const text =
// 'A😀B\n!';`. Which check fails, and what value does it see?
// Expected: The edited run fails with an `AssertionError` at `assert.equal((await
// handle.readFile()).length, 7)`. Restoring `const text = 'A😀B\n';` brings back: text round-
// trips; 7 UTF-8 bytes versus 5 code units; the handle reports fd -1 after its block.

// Exercise 2: Preserve characters and lines across chunks: debug a regression
// A regression made one Example B line read `await writeFile(path, 'A😀B\r\nsecond\n!',
// 'utf8');`. Locate and repair it without editing the check.
// Expected: Before the repair the run fails with an `AssertionError` at
// `assert.deepEqual(await readLines(path), ['A😀B', 'second'])`. Restoring `await
// writeFile(path, 'A😀B\r\nsecond\n', 'utf8');` brings back: lines are A😀B and second,
// without a corrupt replacement character.

// Exercise 3: Refuse accidental overwrite
// Create a file exclusively twice and inspect its unchanged content.
// Expected: second creation rejects with EEXIST; original first remains.

// Exercise 4: Distinguish a missing file
// Read a path known not to exist in the fresh directory.
// Expected: ENOENT rejection.

// Exercise 5: Restrict a learner-supplied fixture name
// Accept report.txt but reject traversal, separators and an absolute path.
// Expected: only report.txt is accepted.

// Exercise 6: Handle an empty text stream
// Stream an empty file with the same decoder and line interface.
// Expected: no lines.

console.log("Implement the six exercises in your saved copy.");

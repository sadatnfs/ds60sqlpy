# c-018: explained solutions

`c-018_solution.c` assembles the "round-trip an owned stream" case through the "transfer binary zero bytes" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A FILE stream buffers I/O and tracks state such as end-of-file and errors. A read operation reports what happened; feof predicts nothing before an attempted read reaches the end. A short read can mean EOF or an error, so inspect stream state appropriately. Writes and close operations can fail, especially when buffered data is flushed. Resource ownership includes closing the stream on every completed path, not merely after the happy-path computation. These examples use tmpfile, which creates an owned temporary stream removed on closure. They do not read or overwrite learner files.

fwrite and fread return element counts, not necessarily byte counts unless element size is one. fseek or rewind changes position; rewind also clears error and EOF indicators. fgetc returns int so every unsigned-char value remains distinct from EOF. fgets reads a bounded line and retains a newline when one fits. fclose releases the stream and may report a final write failure.

## Exercise 1: Round-trip an owned stream: predict an edited check

In worked example 1, change `CHECK(fwrite("abc", 1, 3, f) == 3);` to `CHECK(fwrite("abc", 1, 4, f) == 3);`. Predict whether the CHECK still holds and why, then run and restore.

The unchanged code is worked example 1:

```c
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(fwrite("abc", 1, 3, f) == 3);
rewind(f);
char data[4] = {0};
CHECK(fread(data, 1, 3, f) == 3 && strcmp(data, "abc") == 0);
CHECK(fclose(f) == 0);
```

**Expected:** `Check failed`: `CHECK(fwrite("abc", 1, 4, f) == 3);` is false, although three bytes return and match abc.

**Verify:** Explain which claim `CHECK(fwrite("abc", 1, 4, f) == 3);` makes that the state fails; restoring `CHECK(fwrite("abc", 1, 3, f) == 3);` passes again.

The terminator comes from initialized output storage, not from fread. Binary reads do not automatically append a string terminator.

## Exercise 2: Observe a short read: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(fwrite("ab", 1, 3, f) == 2);`. Explain why it fails although two bytes return and EOF becomes set, then restore it.

The unchanged code is worked example 2:

```c
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(fwrite("ab", 1, 2, f) == 2);
rewind(f);
char data[4];
size_t n = fread(data, 1, 4, f);
CHECK(n == 2 && feof(f) && !ferror(f));
CHECK(fclose(f) == 0);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(fwrite("ab", 1, 2, f) == 2);` again, though two bytes return and EOF becomes set.

**Verify:** Explain why `CHECK(fwrite("ab", 1, 3, f) == 2);` rejects a state that `fwrite("ab", 1, 2, f) == 2` accepts, using your failing and repaired runs.

The count is the primary evidence. EOF explains why the remaining requested bytes were unavailable.

## Exercise 3: Avoid prechecking EOF

Inspect an empty stream before and after a read.

```c
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(!feof(f));
CHECK(fgetc(f) == EOF && feof(f));
CHECK(fclose(f) == 0);
```

**Expected:** EOF is false before the read and true afterward.

**Verify:** Keep a CHECK equivalent to `fclose(f) == 0`. Control edit: `CHECK(fclose(f) != 0);` must fail; then restore it.

A while(!feof(f)) loop can process a nonexistent final record because EOF is discovered by reading.

## Exercise 4: Read a bounded line

Read a newline-terminated line into sufficient storage.

```c
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(fputs("red\n", f) >= 0);
rewind(f);
char line[8];
CHECK(fgets(line, sizeof line, f) != NULL && strcmp(line, "red\n") == 0);
CHECK(fclose(f) == 0);
```

**Expected:** The newline remains in the result.

**Verify:** Keep a CHECK equivalent to `fgets(line, sizeof line, f) != NULL && strcmp(line, "red\n") == 0`. Control edit: `CHECK(fgets(line, sizeof line, f) != NULL && strcmp(line, "red\n!") == 0);` must fail; then restore it.

Trimming a newline is a separate application policy. A full buffer without newline may indicate a partial line rather than a complete record.

## Exercise 5: Clear EOF by rewinding

Reach EOF, rewind and read the first character again.

```c
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(fputc('x', f) != EOF);
rewind(f);
CHECK(fgetc(f) == 'x' && fgetc(f) == EOF);
rewind(f);
CHECK(!feof(f) && fgetc(f) == 'x');
CHECK(fclose(f) == 0);
```

**Expected:** The first character is available again.

**Verify:** Keep a CHECK equivalent to `fgetc(f) == 'x' && fgetc(f) == EOF`. Control edit: `CHECK(fputc('x!', f) != EOF);` must fail; then restore it.

Stream state changes with positioning operations. A prior EOF is not a permanent property of the underlying content.

## Exercise 6: Transfer binary zero bytes

Write and read a byte sequence containing zero.

```c
unsigned char source[] = {1, 0, 2}, out[3] = {0};
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(fwrite(source, 1, 3, f) == 3);
rewind(f);
CHECK(fread(out, 1, 3, f) == 3 && memcmp(source, out, 3) == 0);
CHECK(fclose(f) == 0);
```

**Expected:** All three bytes survive, including the middle zero.

**Verify:** Keep a CHECK equivalent to `fread(out, 1, 3, f) == 3 && memcmp(source, out, 3) == 0`. Control edit: `CHECK(fread(out, 2, 3, f) == 3 && memcmp(source, out, 3) == 0);` must fail; then restore it.

Binary data is length-delimited, not terminated by zero. String functions would incorrectly treat the middle zero as an endpoint.

## After comparison

Write the six bytes `ab\ncd\n` to a `tmpfile()`, rewind, and read with `fgets` into `char line[3]`. Predict the pieces: `ab`, then the newline alone, then `cd`, then the second newline, then NULL at end of file. CHECK that four calls succeed for two lines, and explain why counting `fgets` calls is not counting lines when the buffer is shorter than a line.

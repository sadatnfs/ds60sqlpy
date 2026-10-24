# c-018: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A FILE stream buffers I/O and tracks state such as end-of-file and errors. A read operation reports what happened; feof predicts nothing before an attempted read reaches the end. A short read can mean EOF or an error, so inspect stream state appropriately. Writes and close operations can fail, especially when buffered data is flushed. Resource ownership includes closing the stream on every completed path, not merely after the happy-path computation. These examples use tmpfile, which creates an owned temporary stream removed on closure. They do not read or overwrite learner files.

fwrite and fread return element counts, not necessarily byte counts unless element size is one. fseek or rewind changes position; rewind also clears error and EOF indicators. fgetc returns int so every unsigned-char value remains distinct from EOF. fgets reads a bounded line and retains a newline when one fits. fclose releases the stream and may report a final write failure.

## Exercise 1: Round-trip an owned stream

Write abc, rewind and read three bytes.

```c
FILE *f = tmpfile();
CHECK(f != NULL);
CHECK(fwrite("abc", 1, 3, f) == 3);
rewind(f);
char data[4] = {0};
CHECK(fread(data, 1, 3, f) == 3 && strcmp(data, "abc") == 0);
CHECK(fclose(f) == 0);
```

**Expected:** Three bytes return and match abc.

The terminator comes from initialized output storage, not from fread. Binary reads do not automatically append a string terminator.

## Exercise 2: Observe a short read

Request four bytes from a two-byte stream.

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

**Expected:** Two bytes return and EOF becomes set.

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

Binary data is length-delimited, not terminated by zero. String functions would incorrectly treat the middle zero as an endpoint.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.

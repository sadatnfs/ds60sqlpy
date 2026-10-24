# c-034: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

POSIX file descriptors are small integer handles to open resources. They are not FILE pointers, and their read/write operations do not use the same buffering contract. A pipe provides a byte stream from one endpoint to another. Reads can be short, and EOF occurs only after all write endpoints are closed and buffered bytes are consumed. Forgetting an inherited or duplicated write endpoint can make a reader wait forever. Every descriptor needs a known owner and close point. These examples create only local anonymous pipes and close them within each case; they never open host paths or contact a network.

pipe fills two descriptors: index zero reads and index one writes. read and write return ssize_t, with negative values indicating errors. A robust general loop handles EINTR and partial transfers under a total byte budget. close releases one descriptor reference. dup creates another reference to the same underlying open description, so closing one reference does not necessarily end the stream. POSIX APIs are platform extensions, not ISO C17 itself.

## Exercise 1: Transfer a small pipe payload

Write abc, close the writer and read the bytes.

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(write(fds[1], "abc", 3) == 3);
CHECK(close(fds[1]) == 0);
char out[4] = {0};
CHECK(read(fds[0], out, 3) == 3 && strcmp(out, "abc") == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** Three bytes arrive unchanged.

The tiny write is within the pipe atomic-write bound. General streams still require loops for partial operations.

## Exercise 2: Observe EOF after closure

Close an unused writer and read from its empty pipe.

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(close(fds[1]) == 0);
char byte = 0;
CHECK(read(fds[0], &byte, 1) == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** read returns zero.

Zero is EOF for this positive-sized read, not an error. All writers are closed before waiting.

## Exercise 3: Read a payload in two pieces

Write four bytes and request two bytes at a time.

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(write(fds[1], "abcd", 4) == 4);
CHECK(close(fds[1]) == 0);
char a[3] = {0}, b[3] = {0};
CHECK(read(fds[0], a, 2) == 2 && read(fds[0], b, 2) == 2);
CHECK(strcmp(a, "ab") == 0 && strcmp(b, "cd") == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** The pieces are ab and cd.

A stream does not preserve application record boundaries. The receiver chooses how many bytes to request.

## Exercise 4: Retain binary zeros

Send bytes 1, 0, 2 through a pipe.

```c
int fds[2];
unsigned char data[] = {1, 0, 2}, out[3] = {0};
CHECK(pipe(fds) == 0);
CHECK(write(fds[1], data, 3) == 3);
CHECK(close(fds[1]) == 0);
CHECK(read(fds[0], out, 3) == 3 && memcmp(data, out, 3) == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** All three bytes are preserved.

POSIX reads report lengths and do not interpret null-terminated strings.

## Exercise 5: Account for duplicated ownership

Duplicate the write descriptor, then close both before reading EOF.

```c
int fds[2];
CHECK(pipe(fds) == 0);
int duplicate = dup(fds[1]);
CHECK(duplicate >= 0);
CHECK(close(fds[1]) == 0 && close(duplicate) == 0);
char byte = 0;
CHECK(read(fds[0], &byte, 1) == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** EOF arrives after both references close.

Closing only the original descriptor would leave another writer reference alive.

## Exercise 6: Transfer a bounded record decoder

Read exactly a two-byte tag from a three-byte payload.

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(write(fds[1], "OK7", 3) == 3);
CHECK(close(fds[1]) == 0);
char tag[3] = {0}, value = 0;
CHECK(read(fds[0], tag, 2) == 2 && read(fds[0], &value, 1) == 1);
CHECK(strcmp(tag, "OK") == 0 && value == '7');
CHECK(close(fds[0]) == 0);
```

**Expected:** The tag is OK and one byte remains for the next read.

The caller defines framing. Real protocol code must validate lengths and handle interruption or partial reads rather than assume every call fills its buffer.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.

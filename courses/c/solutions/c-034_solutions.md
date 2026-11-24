# c-034: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference, `c-034_solution.c`, implements all six cases, from the "transfer a small pipe payload" case to the "transfer a bounded record decoder" case, in one `main.c`.

## Mechanism and assumptions

POSIX file descriptors are small integer handles to open resources. They are not FILE pointers, and their read/write operations do not use the same buffering contract. A pipe provides a byte stream from one endpoint to another. Reads can be short, and EOF occurs only after all write endpoints are closed and buffered bytes are consumed. Forgetting an inherited or duplicated write endpoint can make a reader wait forever. Every descriptor needs a known owner and close point. These examples create only local anonymous pipes and close them within each case; they never open host paths or contact a network.

pipe fills two descriptors: index zero reads and index one writes. read and write return ssize_t, with negative values indicating errors. A robust general loop handles EINTR and partial transfers under a total byte budget. close releases one descriptor reference. dup creates another reference to the same underlying open description, so closing one reference does not necessarily end the stream. POSIX APIs are platform extensions, not ISO C17 itself.

## Exercise 1: Transfer a small pipe payload: predict an edited check

Copy worked example 1 into a scratch pad and change `CHECK(close(fds[0]) == 0);` to `CHECK(close(fds[1]) == 0);` inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it.

The unchanged code is worked example 1:

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(write(fds[1], "abc", 3) == 3);
CHECK(close(fds[1]) == 0);
char out[4] = {0};
CHECK(read(fds[0], out, 3) == 3 && strcmp(out, "abc") == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** With `CHECK(close(fds[1]) == 0);` the run stops with `Check failed` at the CHECK on `close(fds[0]) == 0`, because the "transfer a small pipe payload" case no longer shows that three bytes arrive unchanged. Restoring `CHECK(close(fds[0]) == 0);` brings that observation back.

The tiny write is within the pipe atomic-write bound. General streams still require loops for partial operations.

## Exercise 2: Observe EOF after closure: diagnose an edited check

A careless edit changed the CHECK in worked example 2, the "observe EOF after closure" case, so that it reads `CHECK(close(fds[1]) == 0);`. Run the example with that line, explain why the edited CHECK now fails even though the program state still means read returns zero, and restore it.

The unchanged code is worked example 2:

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(close(fds[1]) == 0);
char byte = 0;
CHECK(read(fds[0], &byte, 1) == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `close(fds[0]) == 0`. Once the line reads `CHECK(close(fds[0]) == 0);` again, the "observe EOF after closure" case again shows that read returns zero.

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

Add a fresh distinguishing input for the "transfer a bounded record decoder" case to your own c-034 source. Explain why every access in the case code inside `main` stays within a live object and each owned resource is released. An expected file descriptor failure belongs in the test contract; undefined behavior does not. Keep diagnostics and sanitizer evidence for the "observe EOF after closure" case apart from ordinary output: the fixture proves its stated file descriptor, pipe endpoint and descriptor ownership assumptions, not universal safety.

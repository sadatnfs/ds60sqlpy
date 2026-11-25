# c-034: explained solutions

`c-034_solution.c` assembles the "transfer a small pipe payload" case through the "transfer a bounded record decoder" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

POSIX file descriptors are small integer handles to open resources. They are not FILE pointers, and their read/write operations do not use the same buffering contract. A pipe provides a byte stream from one endpoint to another. Reads can be short, and EOF occurs only after all write endpoints are closed and buffered bytes are consumed. Forgetting an inherited or duplicated write endpoint can make a reader wait forever. Every descriptor needs a known owner and close point. These examples create only local anonymous pipes and close them within each case; they never open host paths or contact a network.

pipe fills two descriptors: index zero reads and index one writes. read and write return ssize_t, with negative values indicating errors. A robust general loop handles EINTR and partial transfers under a total byte budget. close releases one descriptor reference. dup creates another reference to the same underlying open description, so closing one reference does not necessarily end the stream. POSIX APIs are platform extensions, not ISO C17 itself.

## Exercise 1: Transfer a small pipe payload: predict an edited check

In worked example 1, change `CHECK(close(fds[0]) == 0);` to `CHECK(close(fds[1]) == 0);`. Predict whether the CHECK still holds and why, then run and restore.

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

**Expected:** `Check failed`: `CHECK(close(fds[1]) == 0);` is false, although three bytes arrive unchanged.

**Verify:** Explain which claim `CHECK(close(fds[1]) == 0);` makes that the state fails; restoring `CHECK(close(fds[0]) == 0);` passes again.

The tiny write is within the pipe atomic-write bound. General streams still require loops for partial operations.

## Exercise 2: Observe EOF after closure: diagnose an edited check

Worked example 2's CHECK now reads `CHECK(close(fds[1]) == 0);`. Explain why it fails although read returns zero, then restore it.

The unchanged code is worked example 2:

```c
int fds[2];
CHECK(pipe(fds) == 0);
CHECK(close(fds[1]) == 0);
char byte = 0;
CHECK(read(fds[0], &byte, 1) == 0);
CHECK(close(fds[0]) == 0);
```

**Expected:** `Check failed` until the CHECK reads `CHECK(close(fds[0]) == 0);` again, though read returns zero.

**Verify:** Explain why `CHECK(close(fds[1]) == 0);` rejects a state that `close(fds[0]) == 0` accepts, using your failing and repaired runs.

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

**Verify:** Keep a CHECK equivalent to `close(fds[0]) == 0`. Control edit: `CHECK(close(fds[1]) == 0);` must fail; then restore it.

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

**Verify:** Keep a CHECK equivalent to `close(fds[0]) == 0`. Control edit: `CHECK(close(fds[1]) == 0);` must fail; then restore it.

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

**Verify:** Keep a CHECK equivalent to `close(fds[0]) == 0`. Control edit: `CHECK(close(fds[1]) == 0);` must fail; then restore it.

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

**Verify:** Keep a CHECK equivalent to `close(fds[0]) == 0`. Control edit: `CHECK(close(fds[1]) == 0);` must fail; then restore it.

The caller defines framing. Real protocol code must validate lengths and handle interruption or partial reads rather than assume every call fills its buffer.

## After comparison

Write `AB` and `CD` as two separate `write` calls to one pipe and close the write end. Then read with a four-byte buffer in a loop until `read` returns 0, and CHECK that the total is four bytes and the text is `ABCD`, without assuming how many reads it took. Explain why the loop must continue after a short count and stop only on 0 or an error.

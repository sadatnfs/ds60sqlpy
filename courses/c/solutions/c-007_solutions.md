# c-007: explained solutions

`c-007_solution.c` assembles the "compare length and storage" case through the "transfer an empty string" case in one `main.c`.

Compare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).

## Mechanism and assumptions

A C string is a character sequence terminated by a null character. The terminator occupies storage but is not counted by strlen. A character array is not automatically a valid string: its contents must include a terminator within accessible storage before string functions can safely scan it. String literals must not be modified. A writable array initialized from a literal has its own storage. A pointer to a literal has a different mutation contract even when both can be read through const char pointers. Byte strings also do not automatically provide Unicode character indexing.

char word[] = "cat" creates four characters including the terminator. strlen counts bytes before that terminator. sizeof word counts the array storage in this scope. strcmp compares string content; pointer equality compares addresses instead. snprintf limits writes and reports the required length, allowing truncation detection. Reserve capacity for the terminating null byte and never repair a missing bound by hoping the next memory byte is zero.

## Exercise 1: Compare length and storage: change one input

In worked example 1, change `char word[] = "cat";` to `char word[] = "cat!";`. Predict which value the CHECK on `strlen(word) == 3 && sizeof word == 4` sees, then run and restore.

The unchanged code is worked example 1:

```c
char word[] = "cat";
CHECK(strlen(word) == 3 && sizeof word == 4);
```

**Expected:** `Check failed` at `strlen(word) == 3 && sizeof word == 4`; restoring `char word[] = "cat";` passes again.

**Verify:** Name the value that made `strlen(word) == 3 && sizeof word == 4` false, where worked example 1 showed that strlen is 3 while array size is 4.

The fourth byte is the terminator. Forgetting it when allocating an output creates a one-byte overflow risk.

## Exercise 2: Modify owned text: debug a regression

Worked example 2 now has a line reading `word[1] = 'b';`. Repair it so that the result is bat again.

The unchanged code is worked example 2:

```c
char word[] = "cat";
word[0] = 'b';
CHECK(strcmp(word, "bat") == 0);
```

**Expected:** `Check failed` at `strcmp(word, "bat") == 0` until the line reads `word[0] = 'b';` again.

**Verify:** Explain how `word[1] = 'b';` changes the value `strcmp(word, "bat") == 0` tests, using your failing and repaired runs.

The array is writable. Performing the same assignment through a pointer to a string literal would be undefined behavior.

## Exercise 3: Detect bounded truncation

Format hello into a four-character buffer.

```c
char out[4];
int n = snprintf(out, sizeof out, "%s", "hello");
CHECK(n == 5 && strcmp(out, "hel") == 0);
CHECK((size_t)n >= sizeof out);
```

**Expected:** The required length is 5 and stored text is hel.

**Verify:** Keep a CHECK equivalent to `n == 5 && strcmp(out, "hel") == 0`. Control edit: changing `char out[4];` to `char out[5];` must fail it; then restore it.

The return value reports required length, not just bytes stored. Check a negative result before converting to size_t in a general helper.

## Exercise 4: Accept exact capacity

Store cat in a four-character buffer.

```c
char out[4];
int n = snprintf(out, sizeof out, "%s", "cat");
CHECK(n == 3 && strcmp(out, "cat") == 0);
```

**Expected:** The complete text fits with its terminator.

**Verify:** Keep a CHECK equivalent to `n == 3 && strcmp(out, "cat") == 0`. Control edit: changing `int n = snprintf(out, sizeof out, "%s", "cat");` to `int n = snprintf(out, sizeof out, "%s!", "cat");` must fail it; then restore it.

Capacity equal to payload length is insufficient. This destination has one additional character for termination.

## Exercise 5: Compare content rather than pointers

Create two separate arrays containing cat.

```c
char a[] = "cat";
char b[] = "cat";
CHECK(strcmp(a, b) == 0);
```

**Expected:** strcmp reports equality.

**Verify:** Keep a CHECK equivalent to `strcmp(a, b) == 0`. Control edit: changing `char a[] = "cat";` to `char a[] = "cat!";` must fail it; then restore it.

The arrays are distinct objects with equal content. Address equality is the wrong contract for textual equality.

## Exercise 6: Transfer an empty string

Create a one-character array containing only zero.

```c
char empty[1] = {'\0'};
CHECK(strlen(empty) == 0 && sizeof empty == 1);
```

**Expected:** Its string length is zero.

**Verify:** Keep a CHECK equivalent to `strlen(empty) == 0 && sizeof empty == 1`. Control edit: changing `char empty[1] = {'\0'};` to `char empty[2] = {'\0'};` must fail it; then restore it.

Even an empty C string needs a terminator object. A null pointer is absence of an object, not an empty string.

## After comparison

Initialize `char word[] = {'c', 'a', 't'};` and explain as text why `strlen(word)` is undefined: the array holds three bytes and no terminator, so the search runs off the end. Then run the defined form, `char word[] = "cat";`, and CHECK `sizeof word == 4 && strlen(word) == 3`. Finally CHECK that `memchr(word, '\0', sizeof word)` points at `word + 3`, which shows exactly where the terminator lives.

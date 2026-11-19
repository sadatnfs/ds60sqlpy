# c-007: explained solutions

Compare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.

## Mechanism and assumptions

A C string is a character sequence terminated by a null character. The terminator occupies storage but is not counted by strlen. A character array is not automatically a valid string: its contents must include a terminator within accessible storage before string functions can safely scan it. String literals must not be modified. A writable array initialized from a literal has its own storage. A pointer to a literal has a different mutation contract even when both can be read through const char pointers. Byte strings also do not automatically provide Unicode character indexing.

char word[] = "cat" creates four characters including the terminator. strlen counts bytes before that terminator. sizeof word counts the array storage in this scope. strcmp compares string content; pointer equality compares addresses instead. snprintf limits writes and reports the required length, allowing truncation detection. Reserve capacity for the terminating null byte and never repair a missing bound by hoping the next memory byte is zero.

## Exercise 1: Compare length and storage: change one input

Copy worked example 1 into a scratch pad and change `char word[] = "cat";` to `char word[] = "cat!";`. Before running, predict which CHECK fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```c
char word[] = "cat";
CHECK(strlen(word) == 3 && sizeof word == 4);
```

**Expected:** The changed run stops with `Check failed` at the CHECK on `strlen(word) == 3 && sizeof word == 4`. Restoring the original line brings back the worked observation: strlen is 3 while array size is 4.

The fourth byte is the terminator. Forgetting it when allocating an output creates a one-byte overflow risk.

## Exercise 2: Modify owned text: debug a regression

A regression changed one token in worked example 2, so one line now reads `word[1] = 'b';`. Run worked example 2 with that line, use the failing CHECK to locate the defect and repair it without changing the CHECK.

The unchanged code is worked example 2:

```c
char word[] = "cat";
word[0] = 'b';
CHECK(strcmp(word, "bat") == 0);
```

**Expected:** Before the repair the run stops with `Check failed` at the CHECK on `strcmp(word, "bat") == 0`; after it the line reads `word[0] = 'b';` again and the result is bat.

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

The return value reports required length, not just bytes stored. Check a negative result before converting to size_t in a general helper.

## Exercise 4: Accept exact capacity

Store cat in a four-character buffer.

```c
char out[4];
int n = snprintf(out, sizeof out, "%s", "cat");
CHECK(n == 3 && strcmp(out, "cat") == 0);
```

**Expected:** The complete text fits with its terminator.

Capacity equal to payload length is insufficient. This destination has one additional character for termination.

## Exercise 5: Compare content rather than pointers

Create two separate arrays containing cat.

```c
char a[] = "cat";
char b[] = "cat";
CHECK(strcmp(a, b) == 0);
```

**Expected:** strcmp reports equality.

The arrays are distinct objects with equal content. Address equality is the wrong contract for textual equality.

## Exercise 6: Transfer an empty string

Create a one-character array containing only zero.

```c
char empty[1] = {'\0'};
CHECK(strlen(empty) == 0 && sizeof empty == 1);
```

**Expected:** Its string length is zero.

Even an empty C string needs a terminator object. A null pointer is absence of an object, not an empty string.

## After comparison

Return to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.

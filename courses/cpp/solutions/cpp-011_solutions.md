# cpp-011: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A stream is an interface that moves characters between a program and a source or destination. RAII ties resource cleanup to scope exit. EOF means there is no more input, while a bad I/O state means a device operation failed. The loop must ask whether a read succeeded before using the buffer.

## Detailed reasoning

The getline expression reads before the body. With 10-newline-20-newline it succeeds twice; the next attempt discovers EOF and the body does not run. An eof-first loop asks yesterday's state and can reuse yesterday's buffer. For real files, opening failure, clean EOF and a bad device state are different observations. Record the resolved filename before diagnosing a missing file; changing main.cpp's location cannot change the process working directory.

## Worked example 1

```cpp
std::istringstream input("10\n20\n"); auto lines=read_lines(input);
```

Expected: Exactly two lines, with no extra stale third line.

## Worked example 2

```cpp
std::istringstream input("30"); auto lines=read_lines(input);
```

Expected: The final line without newline is still read once.

## Exercise 1: Trace successful reads

Read the literal 10-newline-20-newline fixture.

**Expected:** Two records [10,20].

**Reasoning:** getline determines whether a record exists.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Handle empty input

Run read_lines on an empty string stream.

**Expected:** Zero records, ordinary EOF.

**Reasoning:** Empty input is not automatically an I/O device error.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Write an owned file

In a new scratch directory write two lines, close, reopen and read.

**Expected:** The reopened bytes represent 10 and 20 exactly once.

**Reasoning:** Close or flush before reading through a second stream.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair eof-first looping

Compare while(!eof()) with the supplied successful-read loop.

**Expected:** The repaired loop has two records and no stale extra line.

**Reasoning:** EOF becomes known only after a read attempts the boundary.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check open failure

Open missing-file.txt for input in a new empty scratch directory.

**Expected:** is_open false or stream failure; report the path and stop.

**Reasoning:** A missing file must not silently become an empty successful report.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer the path contract

Run from two working directories with the same relative filename.

**Expected:** Different resolved locations; explicit supplied path selects one file.

**Reasoning:** The current directory, not main.cpp location, anchors relative paths.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

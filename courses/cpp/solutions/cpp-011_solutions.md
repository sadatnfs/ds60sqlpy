# cpp-011: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A stream is an interface that moves characters between a program and a source or destination. RAII ties resource cleanup to scope exit. EOF means there is no more input, while a bad I/O state means a device operation failed. The loop must ask whether a read succeeded before using the buffer.

## Detailed reasoning

The getline expression reads before the body. With 10-newline-20-newline it succeeds twice; the next attempt discovers EOF and the body does not run. An eof-first loop asks yesterday's state and can reuse yesterday's buffer. For real files, opening failure, clean EOF and a bad device state are different observations. Record the resolved filename before diagnosing a missing file; changing main.cpp's location cannot change the process working directory.

<!-- depth:start -->
## Streams, EOF and resource lifetime

A stream has both data and state. getline attempts to extract the next line and reports whether that extraction succeeded. The loop condition must test the result of the read before using the line. The pattern while(!input.eof()) checks a state that may not become true until a read attempts to go beyond the available input, so it can process a stale or failed buffer on the final iteration.

A newline is a separator, not necessarily a required terminator for the final record. The first complete program reads10 and 20 from a string containing two newline separators. The second reads30 from a final line with no trailing newline. Both are successful line extractions. A completely empty stream yields no line, while a stream containing one newline yields one empty line. Your data grammar must decide whether an empty record is valid or rejected.

EOF and bad I/O are different conditions. Reaching the end of an otherwise valid input is expected. A device or stream-buffer failure needs an error path. The reference checks bad() after the loop to distinguish that failure from ordinary exhaustion. A file reader must also check whether opening the file succeeded before treating it as a useful source; an unopened stream should not be reported as a valid empty dataset.

RAII ties the file resource to the stream object's lifetime. An ifstream closes its resource when destroyed, including during exception unwinding. That prevents a forgotten close on one error path, but it does not validate the data read or guarantee a successful write. For output, inspect the stream state after writing and closing when the contract needs confirmation that output was accepted by the stream.

A relative file path is resolved against the process working directory. Compiling a source in one folder does not make runtime reads relative to that source file. Record the input path and working directory when diagnosing a missing file. The browser runner stages a single source and has a controlled filesystem; a host file exercise must use an owned fixture directory and the explicit commands in the compile/run guide.

## Debugging the contract

If the last record repeats, look for an eof-before-read loop. If a final unterminated line disappears, inspect whether the parser requires a newline accidentally. If a missing file reports zero accepted rows and success, the open failure was probably ignored. If only Windows input fails, define carriage-return handling explicitly rather than silently altering bytes without a format contract. Test empty input, an empty line and no-final-newline as three different fixtures.
<!-- depth:end -->

## Worked example 1

```cpp
std::istringstream input("10\n20\n");
auto lines = read_lines(input);
```

Expected: Exactly two lines, with no extra stale third line.

## Worked example 2

```cpp
std::istringstream input("30");
auto lines = read_lines(input);
```

Expected: The final line without newline is still read once.

## Exercise 1: Trace successful reads

Read the literal 10-newline-20-newline fixture.

**Expected:** Two records [10, 20].

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

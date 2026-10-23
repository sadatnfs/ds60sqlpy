# cpp-001: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/cpp-001.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

A C++ source file is editable text. Compilation checks language rules and translates each translation unit to object code. Linking joins object code and library definitions into an executable. Running starts a process from that executable. A failure in one phase is not evidence that later phases ran.

The terminal is an interface for requesting a program and reading its streams; a displayed transcript is not itself a command you have executed. Paths identify files relative to a working directory or an absolute location. This reading lesson uses supplied transcripts so no compiler installation is required. Keep a distinction among what source states, what a tool accepted and what a process actually observed.

- **source:** human-editable C++ text, usually .cpp
- **object file:** compiled code that still needs linking
- **executable:** a linked program file
- **stdout/stderr:** separate normal-output and diagnostic streams
- **exit status:** the process result code, with0 normally signaling success

## Worked example / walkthrough

### Worked example 1: Follow one successful request

Changing hello.cpp affects a future build. It cannot alter a previous stdout transcript.

```text
input: hello.cpp
compile: hello.o
link: hello
run stdout: hello, learner
run exit: 0
```

**Expected:** There are four phases and one successful process observation.

### Worked example 2: Stop at the first failed phase

A tool reporting an error did run; the program being compiled did not thereby run.

```text
compile: error: expected semicolon
object file: not produced
link: not run
process: not run
```

**Expected:** This is a compile failure, with no runtime exit evidence.

## Exercises and explanatory solutions

### Exercise 1: Name each artifact

**Inputs/evidence:** For cpp-001 Exercise 1, hello.cpp,hello.o,hello and hello, learner.

**Expected result/shape:** For cpp-001 Exercise 1, source/object/executable/output in that order.

**Verify:** For cpp-001 Exercise 1, label all four without treating the executable as source.

The suffixes are conventional clues, but the build transcript establishes provenance. A printed greeting is data from a process, not the executable file itself.

### Exercise 2: Read a relative path

**Inputs/evidence:** For cpp-001 Exercise 2, working directory course;relative path lessons/hello.cpp.

**Expected result/shape:** For cpp-001 Exercise 2, the intended file is course/lessons/hello.cpp.

**Verify:** For cpp-001 Exercise 2, draw the joined path and explain why changing the working directory changes a relative path.

A relative path is interpreted against a base. Quoting protects spaces but does not change which base directory a tool uses.

### Exercise 3: Classify a syntax error

**Inputs/evidence:** For cpp-001 Exercise 3, compiler rejects std::cout line; no object emitted.

**Expected result/shape:** For cpp-001 Exercise 3, compile failure; linking and learner-process execution not established.

**Verify:** For cpp-001 Exercise 3, state which artifact is absent and avoid claiming a runtime crash.

The compiler diagnoses syntax before it can produce valid object code. This is different from a process failing after a successful build.

### Exercise 4: Classify a link error

**Inputs/evidence:** For cpp-001 Exercise 4, hello.o exists; linker says a called function has no definition.

**Expected result/shape:** For cpp-001 Exercise 4, link failure; no new executable established.

**Verify:** For cpp-001 Exercise 4, identify the missing definition or omitted object as the next check.

A declaration tells the compiler a signature; the linker still needs a matching definition. This is not solved by ignoring the link command result.

### Exercise 5: Read a runtime failure

**Inputs/evidence:** For cpp-001 Exercise 5, program prints started then exits2.

**Expected result/shape:** For cpp-001 Exercise 5, the process ran and failed its declared contract despite producing text.

**Verify:** For cpp-001 Exercise 5, record both started and exit2; do not call output alone success.

Diagnostic text can precede a failure. A verifier must inspect the status as well as expected values, and a partial output stream cannot make a failing process green.

### Exercise 6: Transfer the phase trace

**Inputs/evidence:** For cpp-001 Exercise 6, old executable prints hello, learner; source now says hello, reviewer; no rebuild.

**Expected result/shape:** For cpp-001 Exercise 6, the old executable still prints hello, learner.

**Verify:** For cpp-001 Exercise 6, name the missing build step and keep source/build/run receipts separate.

Editing text does not mutate existing machine code. Rebuild and then run the resulting target before expecting the new behavior.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.

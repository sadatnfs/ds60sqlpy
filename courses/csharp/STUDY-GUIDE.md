# C# study guide

All 48 C# lesson guides link here for the steps that are the same in every chapter:
- how the classroom compiles a pad
- how the starter, worked examples and reference relate
- how to trace a program
- how to record exercise evidence
- how to build a regression case
- how to use hints and an AI tutor
- how to compare your work with the explanation

Each lesson guide keeps only what applies to its own programs.

## Running a lesson

The Linux Docker classroom saves your pad as `Program.cs` and compiles it in a fixed .NET 10 console project. C# 14 is the language version that matches that SDK. The project turns on implicit usings and nullable reference types, so a nullable warning is real feedback about your code and not noise from the classroom.

The pad accepts only the source file. You cannot add your own project file, NuGet packages, command-line arguments or interactive input. Code that needs a web host, a database server or a desktop UI belongs in a separately labeled project lab, and the lesson guide names that lab when a task needs it.

The worked examples and the reference declare an explicit `internal static class Program` with a `Main` method, so you can see where execution starts. They do not use top-level statements. The helper `Check(condition, reason)` throws `InvalidOperationException` when its condition is false. Unlike `Debug.Assert`, which is compiled out of Release builds, `Check` is ordinary code and runs in every build configuration.

## Starter, worked examples and reference

The learner file in `lessons/` contains no answers. It lists the six tasks as comments, and its `Main` throws `NotImplementedException` so an unfinished attempt can never look complete. In your saved pad, replace that throw with your own implementation.

Each worked example in a guide is a complete program. If you want to run one, change an input or break a check on purpose, copy it into its own exploratory pad, one example at a time. The executable reference in `solutions/` combines both examples and every executed task answer into a single program, each in its own block.

When every check passes, nothing is printed for them. The lesson marker, such as `csharp-001: passed`, appears only after every check has finished. The marker shows that the program ran those fixtures. It does not show that you understood them. You show that by explaining the mechanism and the outcome of all six tasks.

## Tracing a program

Follow the statements in the order the program runs them, which is not always the order they appear in the file. For each statement, note three things:
- which variables and objects already exist before it runs
- which expression produces a new value
- which call changes a field, a collection or other shared state

Write your trace before you run the program, then compare it with what actually happens.

There are two kinds of failure, and they need different repairs. Decide which one you have before you change anything:
- **Compile error.** The compiler reports a diagnostic such as `CS0029` and the program never runs, so there is nothing to observe at runtime. Read the first diagnostic before the others, because the later ones often follow from it.
- **Runtime failure.** A check throws while the program is running. Record the exception type, the first incorrect value and the smallest input that produced it.

## Recording exercise evidence

Every lesson has six tasks:
1. Predict and explain.
2. Guided modification.
3. Independent implementation.
4. Diagnose a plausible bug.
5. Boundary and edge cases.
6. Transfer and design.

For each task, keep a short table with four columns:
- the input or starting state
- your prediction
- the value, exception or diagnostic you observed
- the rule that explains any difference

The worked examples show how a mechanism works. The independent and transfer tasks ask for your own design and explanation, so copying an example does not answer them.

## Building a regression case

A good regression case is an input where the rule you intended and a plausible wrong rule give different results. After you fix a bug, run both the original example and that smallest counterexample.

Do not catch an exception and return a plausible default unless the contract explicitly says what that default means. When an example owns a stream, a timer, a task or another disposable resource, keep its `using` or `finally` block and its exception path visible in the code. Do not hide them behind a helper that swallows the failure.

## Hints and the AI tutor

Each guide has three hints:
1. Reproduce Example A unchanged.
2. Find the first line where Example B behaves differently.
3. Test your task 3 attempt against the lesson's pitfalls.

Use them in order, and stop as soon as you are unstuck.

The fenced prompt at the end of each guide is written for an AI tutor. It names the guide, the starter and the prerequisites. It tells the tutor to ask for your prediction before running anything and to keep the reference files closed until you show an attempt. Paste it exactly as written so the tutor follows the same order.

## Self-check routine

Before you move on:
- Explain the lesson's vocabulary without reading the definitions.
- Rebuild a small example from a blank file, using an input the chapter did not use.
- Name one cost or limitation of the technique.

Save your working pad and your notes, because later chapters build on these contracts. Each guide adds questions about its own mechanism.

## Comparing with the explanation

Open a lesson's explanation file only after you have made your own attempt. Where a reference answer exists, it runs as a labeled `Task N` block in the reference program. Where none exists, the explanation says so. After reading it, close it and rebuild one boundary case from memory. Then name the check that would reject a plausible wrong implementation.

## Open transfer tasks

Task 6 in every lesson is a design task with more than one acceptable answer. When the explanation has no single reference answer:
1. Start your design from your task 3 answer and the lesson's mechanism.
2. Write down what your design guarantees.
3. Name one limitation of your choice.

A reviewer should be able to check your guarantee with a small input.

## Sources and execution boundary

The prose, small fixtures and task designs in every lesson are original. The documentation links in each guide, usually to Microsoft Learn, give more API detail. The classroom never fetches them. These are four separate achievements:
- reading a guide
- compiling a reference
- running its checks
- completing an external project lab

A passing reference program on Linux does not show how the code behaves on another platform or host.

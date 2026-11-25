# Swift study guide

Every Swift lesson guide links here for the routine that is the same in all 48 chapters: how the classroom compiles a pad, how the starter, worked examples and reference relate, how to trace a program, how to record exercise evidence, how to build a regression case, how to use hints and an AI tutor, and how to compare your work with the explanation. The lesson guides keep only what is specific to their own programs.

## Running a lesson

The Linux Docker classroom compiles the saved pad as `main.swift` with Swift 6 language checking. The fixed compiler command uses `-parse-as-library -swift-version 6`, so a program needs an explicit `@main` type whose `static func main() async throws` is the entry method. Top-level statements outside that type are rejected under this compile contract.

The worked examples use the standard library and portable Foundation. `precondition` makes a violated invariant stop the process with a failure status, and it stays active under the classroom settings. The pad accepts one source file. It does not accept command arguments, interactive input, package installation or multi-file uploads.

SwiftUI, UIKit, AppKit, Apple simulators and app signing belong to the separately prepared macOS and Xcode project labs, never to the Linux pad. When a lesson's tasks need those surfaces, its guide says so and names the fixture.

## Starter, worked examples and reference

The learner file in `lessons/` is answer-free. It lists the six tasks as comments and stops with `fatalError` so an unfinished attempt can never look complete. Replace that stop with your own implementation in your saved pad.

Each worked example in a guide is a complete program. Copy one at a time into a separate exploratory pad if you want to run it, change an input or break a check on purpose. The executable reference in `solutions/` combines both examples and every executed task answer into one program.

Successful checks print nothing. The lesson marker, such as `swift-001: passed`, appears only after every check has completed. The marker is execution evidence for those fixtures. It is not an assessment of your understanding, which you show by explaining the mechanism and the six task outcomes.

## Tracing a program

Read the operations in dependency order. For each line, record which values exist before it runs, which expression produces a new value and which operation changes stored state. Write the trace before you run the program, then compare.

Separate the two kinds of failure. When the compiler rejects the source, no runtime observation exists yet: read the first diagnostic before the later ones, because later errors often follow from the first. When a check fails during execution, preserve the first incorrect value and the smallest input that produced it. The repairs differ, so name which kind you are looking at before changing anything.

## Recording exercise evidence

Every lesson has six tasks: predict and explain, guided modification, independent implementation, diagnose a plausible bug, boundary and edge cases, and transfer and design. For each task, keep a short table with four columns: the input or initial state, your prediction, the observed value or diagnostic, and the rule that explains the difference.

The worked examples establish mechanisms. The independent and transfer tasks ask for your own representation and explanation, so a copied example is not an answer to them.

## Building a regression case

A useful regression case separates the intended rule from the tempting wrong rule: it is an input where the two rules produce different results. After a repair, run both the original example and the smallest counterexample.

Do not convert an error into a plausible default unless the contract explicitly gives that default a meaning. When an example owns a file, a task or another resource, keep its cleanup and its failure propagation visible in the code rather than hiding them behind a helper that swallows errors.

## Hints and the AI tutor

Each guide has three progressive hints. The first asks you to reproduce Example A unchanged. The second asks you to find the first line where Example B behaves differently. The third asks you to test your task 3 attempt against the lesson's pitfalls. Use them in order and only as far as you need.

The fenced prompt at the end of each guide is written for an AI tutor. It names the guide, the starter and the prerequisites, asks the tutor to request your prediction before running anything, and keeps the reference files closed until you have shown an attempt. Paste it as written so the tutor follows the same order.

## Self-check routine

Before moving on, explain the lesson's vocabulary without reading the definitions, rebuild a small example from a blank file with an input the chapter did not use, and state one cost or limitation of the technique. Save the working pad and your notes; later chapters build on these contracts. Each guide adds questions specific to its own mechanism.

## Comparing with the explanation

Open a lesson's explanation file only after your own attempt. Where a reference answer exists, it runs as a labeled `Task N` block in the reference program; where none exists, the explanation says so plainly. After reading, close it and rebuild one boundary case from memory, then name the check that would reject a plausible wrong implementation.

## Open transfer tasks

Task 6 in each lesson is a design task with more than one acceptable answer. When no single reference exists, build your design from the task 3 answer and the lesson's mechanism, write down what your design guarantees and state one limitation of your choice. A reviewer should be able to check the guarantee with a small input.

## Sources and execution boundary

The prose, small fixtures and task designs in every lesson are original. The documentation links in each guide give additional API detail; the classroom never fetches them. Reading a guide, compiling a reference, running its checks and completing an external Apple project are distinct achievements, and a passing portable reference does not establish platform behavior.

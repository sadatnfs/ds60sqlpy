# web-031: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

PHP is a programming language whose interpreter executes source instructions. In the classroom, a Linux CLI worker runs one file and captures its output. On a web server, a PHP runtime can instead receive request context and produce an HTTP response. These environments share language syntax but expose different inputs and lifecycle behavior. Printing a string that looks like HTML does not turn a CLI process into a web server.

PHP source begins with an opening tag, and statements commonly end with semicolons. Variables begin with a dollar sign. A comment explains source without executing it. Echo writes output; it does not return a value from a function or save data to a database. We start with literal strings and a tiny computed value so each step is visible.

Use a pure PHP file beginning with `<?php`, followed by `declare(strict_types=1);` before other statements. Strict typing affects certain scalar type coercions at function call boundaries; it does not turn PHP into a statically typed language. Omit the closing tag in a pure PHP file to avoid accidental trailing output. Syntax errors occur before the intended program can run, while runtime errors occur during execution.

## Exercise 1: Predict which characters in the greeting source appear in output.

The opening tag and echo keyword do not appear; the string content does.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Change the planned minutes while preserving the label.

Only the numeric portion changes.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Write a PHP program that prints a study topic and computed duration.

The program runs in the CLI worker and produces two clearly labeled values.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a missing semicolon as a parse error.

The interpreter cannot execute the intended statement sequence until syntax is repaired.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Print literal angle brackets and explain the output surface.

The CLI displays text; it does not automatically render a web page.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Compare the CLI lifecycle with a server request lifecycle.

A CLI process receives its prepared inputs; a server integration supplies HTTP context and response handling.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

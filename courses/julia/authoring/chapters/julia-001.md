## The execution model

Julia evaluates expressions to values. A value has a type, such as an integer, floating-point number or string. A name is a binding to a value. Assignment changes that binding; it is not a mathematical equation that must remain true after later assignments. This distinction is the first tool for explaining what a program actually did.

The classroom executes a source file called `main.jl` in a fresh Julia process. It does not preserve variables from an earlier Run. Saving a source draft or note is separate from retaining a running interpreter. A script also differs from the interactive REPL: a bare expression can be displayed automatically in the REPL, while a script generally needs `println` or another output operation to make a result visible.

The examples group instructions inside a named function. `function` starts its definition and `end` closes it. Calling the name with parentheses performs the instructions. The `worked_a()` line at the bottom makes that call explicit. `@test` checks a stated expectation and causes failure if it is false. You will study functions and tests in more depth later; here they provide a clear starting point and visible correctness checks.

## Worked case A: trace a calculation

The program binds two counts, adds them, and prints both a label and the result. `println` inserts a newline after its arguments. The type check shows that the sum is an integer in this prepared environment. Printing a value does not change the value or certify that the numbers represent the intended real-world quantity.

{{WORKED_A}}

## Worked case B: rebinding a scalar

The second program assigns one integer binding to another, then rebinds the original name. The second name retains the earlier integer. This example concerns immutable scalar values; arrays and other mutable objects require the aliasing rules introduced later. Do not generalize this scalar trace into a claim that assignment always copies a whole object.

{{WORKED_B}}

## Read an error as evidence

A misspelled name produces an undefined-variable error. A type mismatch can produce a method error when no applicable method exists. Julia's error report points to a source location and stack of calls. Start at the first relevant line in your submitted code, reproduce the failure with small inputs, and compare it with the expected intermediate values. Repeatedly pressing Run without changing the explanation does not provide new evidence.

Julia compiles specialized code for operations and argument types as it is needed. A first call can include compilation work that a later call in the same process avoids. The classroom's fresh-process boundary therefore matters for timing. The initial startup or first function call is not a clean measurement of steady-state numerical throughput. Performance lessons later separate these costs.

## A reproducible first investigation

Keep source, inputs, expected observations and actual output together. Use small literal data initially so a result can be checked by hand. Add a changed input only after the original trace is understood. A passing assertion confirms the statement for those inputs; it does not establish a general proof or the correctness of an external dataset.

The worker supplies Julia and its prepared scientific packages. No host Julia installation is required for ordinary classroom use. An optional external project can use its own Julia installation and project manifest, but that is a separate environment with its own package and version checks. These lessons name the classroom contract so a learner can reproduce the examples without hidden REPL state.

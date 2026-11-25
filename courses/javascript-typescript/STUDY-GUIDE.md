# JavaScript and TypeScript study guide

Every lesson guide in this track links here for the operating steps that are the
same in all 66 lessons. The lesson guides keep only what is specific to their
own programs: the mental model, worked examples, exercises, hints and the
mistakes that lesson invites. Read this page once, then return to it when a
lesson link points at a section.

## Running Node lessons

The JavaScript lessons use the prepared Node 24.22.3 profile. The classroom
saves your pad as an ES module named `main.mjs` and runs it with Node. A
prepared native environment uses the same command, `node main.mjs`, on
PowerShell and POSIX shells. The programs use only built-in Node and ECMAScript
APIs. Browser APIs such as `document` and `window` have separate host
requirements and are absent in Node.

## Running TypeScript lessons

The TypeScript lessons use the prepared TypeScript 5.9.3 profile. The classroom
saves `main.mts`, checks it with strict NodeNext resolution, `noEmitOnError` and
an ES2022 target, then runs `compiled/main.mjs` on Node 24.22.3 with Node
typings 24.10.0. Compilation and execution are separate stages: a compiler
diagnostic stops the run before any JavaScript exists, and a clean compile says
nothing about data that arrives at run time. Types are erased and do not
validate external JSON.

## Browser reading lessons

Lessons js-029 through js-031 are browser reading and practice lessons. Node has
no `document` or `window`, so their exercises use the separate checked-in HTML
fixtures described in each guide. Record the visible change, where focus lands
and any live-region text for each interaction. The manifest deliberately makes
no Node execution claim for these DOM examples.

## Saved copies and the success receipt

Save your own learner copy under the ignored `.learning/expansion/<lesson-id>/`
folder or in a saved classroom pad before editing. Each worked program includes
its helper definitions, so it runs on its own. The reference solution puts the
six exercises in separate scopes, so a task cannot silently rely on a variable
from a previous task.

A successful assertion is silent. The final JSON receipt, such as
`{"checks":1,"status":"passed"}`, reports how many exercise blocks completed. A
failing assertion must end in a failed process with an `AssertionError`, never
in a generic success message. When an exercise asks you to make a check fail on
purpose, restore the original line and confirm the receipt returns before you
continue.

## Predicting before you run

Write a prediction before every run. A useful prediction names an expected value
or a failure category, not merely a claim that the program should work. Start
from the entry point and list the values that exist before each operation, then
write down the first observation that would disprove your explanation.

Three distinctions catch most wrong predictions: a value versus a reference to an
object, a returned Promise versus its eventual result, and a compile-time type
versus a runtime check. For a loop, write the state before and after one
iteration. For a callback, name the caller and the arguments it supplies. For an
asynchronous operation, name who starts it, who awaits it and who owns cleanup.
These small traces make a failure local: you compare the first incorrect state
instead of guessing from a much later symptom.

## Using the hints

Read one hint at a time and attempt the exercise again before reading the next.
If a discrepancy involves scheduling, replace unrelated work with a small trace
array and await the exact completion you intend to observe. Ask a tutor for one
hint about the first incorrect assumption before opening the reference.

## Diagnosing a failure

Keep the smallest fixture that distinguishes the intended behavior from a
tempting alternative. Read the assertion message and inspect the input, return
value and state at that point. Do not remove a failing check just to reach the
success receipt. Preserve the original failure, repair the responsible
assumption, then rerun the normal path and the negative case.

If a host API is absent, confirm the actual host and version before changing the
algorithm. A successful parse does not prove that an API exists, compiler
success does not prove that external data satisfies a type, and a browser
interaction needs browser evidence. For resource-owning examples, inspect
cleanup after failure as carefully as the happy path.

## After comparing with the solution

Return to your saved implementation and repeat a case with different values.
Keep compiler diagnostics, process output and browser observations separate. Do
not suppress a failing assertion or use a type assertion to declare an
unvalidated value safe. Resource-owning examples must finish cleanup even when
work fails. Describe each result with its actual host and fixture scope rather
than as production acceptance.

## Sources and validation

Each guide links the official language or host reference it relies on. Fixtures
and exercises are original course material. The
[validation guide](../../docs/validation.md) describes how the references are
run. No default lesson installs dependencies, downloads a model or contacts a
shared service.

## D3 browser preview

The D3 lessons, js-043 through js-066, run in the classroom's JavaScript browser
preview. The prepared preview supplies D3 7.9.0 as the global `d3`, an empty
`#chart` container and an `#output` text region, and it supports top-level
`await` through an asynchronous wrapper. Worked example 2 in each guide is a
complete program: paste the whole block into the preview and its marks appear in
`#chart`. Worked example 1 is a short self-contained snippet whose result
appears in the console.

The examples do not import modules, fetch datasets, use a CDN or contact an
external service. All data is small, synthetic and present in the source. Node
has no DOM and is not the execution host for these lessons. No reference needs
cookies, credentials, host files or engine access.

## D3 completion and checks

Save your own pad before editing and run the learner source after implementing
its tasks. A completed reference prints `<lesson-id> D3 complete` only after its
executable checks finish. A thrown `Error` signals a failed check;
`console.assert` alone is not a reliable completion contract. A browser
observation proves that this source ran in this preview. It is not a trusted
backend verifier or a guarantee of statistical correctness, accessibility or
mastery.

The visual output belongs inside `#chart`. Use `.text()` or `textContent` for
untrusted labels, never HTML interpolation. The preview is recreated for each
run, but reusable components should still bound and clean up long-lived
listeners, timers and animations.

## D3 debugging checkpoints

Keep three checkpoints separate: the records after parsing, the domain and
geometry after transformation, and the visible marks after rendering. A chart
can look plausible while silently dropping records or using the wrong scale.
Inspect counts, IDs, finite coordinates and expected values before adjusting
colors. A missing mark may come from invalid input, an empty selection, an
undefined scale result or clipping outside the `viewBox`.

When an exercise gives you a controlled failure, keep that failing case while you
repair the program. Do not remove an assertion or widen a scale merely to hide a
wrong input. Decide whether a changed value should affect the data, an encoding,
a layout or only presentation.

## D3 accessibility review

Give each visualization a descriptive title and a short text summary of the main
result. Keep a table or list when exact values matter. Do not encode a critical
category only through color; use labels, shapes or position. Interactive
controls need keyboard operation and visible focus, and motion should respect
the reduced-motion preference. Automated DOM checks support, but do not
replace, a real keyboard and assistive-technology review.

## D3 statistical meaning

A chart makes a claim, so state the population, units, aggregation,
missing-value policy and, where relevant, uncertainty. Synthetic points
illustrate a mechanism and do not establish a real-world finding. A good
visualization makes a valid claim easier to inspect; it should not make a weak
claim look certain.

## Retrieval practice

Close the solution before a retrieval attempt. Reconstruct one example from a
blank pad, change one input and predict the result before running it, then
explain when the mechanism is the right tool and when its cost or host
requirements favor another design. Keep your source and your observation
separate from the explanation so you, or a later reader, can reproduce the case.
A copied program is useful rehearsal; a fresh case demonstrates transfer.

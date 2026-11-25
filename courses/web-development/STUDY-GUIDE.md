# Web development study guide

Every web lesson guide in this track uses the same classroom surfaces, the same
six-exercise structure and the same review routine. This page explains those
shared rules once. Each lesson guide keeps only what belongs to its own
mechanism: the mental model, worked examples, a contrast case, the exercises,
the mistakes that lesson invites and a retrieval task about that lesson.

Lessons web-001 to web-030 are HTML documents, web-031 to web-056 are PHP
programs and web-057 to web-060 are Markdown design worksheets.

## HTML preview

Choose **HTML browser preview** and work in the lesson's
`courses/web-development/lessons/web-0NN.html` file. Each file is one complete
HTML document with embedded CSS and, where a lesson teaches it, inline
JavaScript.

The preview is offline. It cannot contact a server, submit a real form or load
external fonts, scripts, images or stylesheets, so every fixture a lesson uses
is inline and synthetic. If a feature seems to do nothing, check the console
for a blocked request before assuming your code is wrong.

Save your attempt before you compare it with the reference. The
**How to run lessons** section of the [subject README](README.md) explains Live
preview, the viewport presets and what a reference check does not show.

## PHP CLI

Choose the **PHP CLI** worker and work in the lesson's
`courses/web-development/lessons/web-0NN.php` file. The worker stages it as
`main.php` and runs it in a bounded Linux process with PDO SQLite available.

Every input is a small synthetic value written in the file. Each run is a fresh
process: nothing in memory, no session and no in-memory SQLite database
survives to the next run. These CLI runs are not persistent HTTP requests, so
headers, cookies, redirects and server lifecycle are modelled as values rather
than observed on the wire. The [subject README](README.md) lists what the pad
does not provide.

Each starter defines a `check()` helper that throws when its condition is
false. Add one `check()` call per case you test, and do not delete a failing
check to make a run look clean.

## Worksheets

Lessons web-057 to web-060 are design worksheets saved as
`courses/web-development/lessons/web-0NN.md`. The classroom does not start a
server, install packages or control Docker, so a command in these lessons is a
proposal until you deliberately run it in your own disposable project.

The optional lab is `courses/web-development/fixtures/php-http-lab/`. Read its
README before preparing it, run it only from your own learner copy and never
expose it to the internet. The lab gives real request evidence only when you
run it on purpose; otherwise your evidence is the worksheet itself: the
prediction, the design and the limits you state.

## Solutions

Each lesson has an explanatory solutions file in
`courses/web-development/solutions/`. Attempt every exercise first. The answers
explain the lesson's synthetic fixtures; they do not show that your own work,
or any deployment, passed.

Exercises that ask you to predict, explain, compare or diagnose keep their
expected answers in the solutions file. The other exercises show the evidence
to look for directly in the guide. A saved completion marker records your own
progress; it is not a certification.

## Debugging HTML

Keep the failing source, the viewport width and what you observed, then repair
one cause at a time. A browser can recover malformed HTML, silently ignore a CSS
declaration or display a plausible layout with the wrong reading order, so
inspect the element and its computed styles in the developer tools instead of
trusting the rendering alone. Retest at the width where the failure appeared.

## Debugging PHP

Keep the failing source, its input and the exact output, then repair one cause
at a time. A parse error means no statement ran; a thrown `check()` names the
case that failed. PHP can print correct-looking text while missing an
invalid-input branch, so rerun the empty, wrong-type and boundary cases after
every fix, not only the case you just repaired.

## Debugging Markdown

A plausible plan or one successful request can hide an untested failure path.
Record each request, response and stored state you observe or propose, and
repeat the original failing case after every change. When a claim has no
evidence yet, move it to the limits section instead of deleting it.

## Review loop

Close the worked answers and explain the lesson's key terms without using the
terms as their own definitions. Rebuild worked example 1 from a blank pad or
worksheet, then try one new value, one empty or missing case and one unusual
boundary. Before running each one, state which result would disprove your
explanation.

If you can reproduce an output but cannot explain why it happens, return to the
lesson's direct prerequisites or its worked examples before moving on.

## References

Each HTML and PHP lesson has a runnable reference in
`courses/web-development/solutions/` that prints a success line only after its
own `check()` calls pass. Open it only after saving your attempt, and compare
decisions rather than identifiers. A different implementation is acceptable
when it shows the same behavior and rejects the same invalid cases.

A reference checks only its named synthetic cases. For HTML, its success
message is not an accessibility audit or proof of responsive behavior at every
size. For PHP, server lifecycle, persistence, concurrency and security need
their own integration evidence. The Markdown worksheets have no executable
reference; compare your worksheet with the solutions file instead.

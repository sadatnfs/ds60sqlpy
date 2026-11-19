# web-031: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-031.md`.

## Exercise 1: Predict which characters in the greeting source appear in output.

**Expected answer:** The opening tag and echo keyword do not appear; the string content does.

**Why:** The `<?php` tag and `echo` are PHP syntax, so only the string's characters, including the newline written as `\n`, reach the output.

## Exercise 2: Change the planned minutes while preserving the label.

**Expected evidence:** Only the numeric portion changes.

**Why:** The label is a separate string literal, so changing `$minutes` alters only the number that concatenation inserts.

## Exercise 3: Write a PHP program that prints a study topic and computed duration.

**Expected evidence:** The program runs in the CLI worker and produces two clearly labeled values.

**Why:** Named values and one computation keep the program readable and let you verify the output by hand.

## Exercise 4: Diagnose a missing semicolon as a parse error.

**Expected answer:** The interpreter cannot execute the intended statement sequence until syntax is repaired.

**Why:** PHP parses the whole file before running it, so a syntax error stops execution and the reported line is often the one after the missing semicolon.

## Exercise 5: Print literal angle brackets and explain the output surface.

**Expected evidence:** The CLI displays text; it does not automatically render a web page.

**Why:** The CLI writes plain text to standard output, so angle brackets are printed as characters; no browser parses them as HTML.

## Exercise 6: Compare the CLI lifecycle with a server request lifecycle.

**Expected answer:** A CLI process receives its prepared inputs; a server integration supplies HTTP context and response handling.

**Why:** A server integration supplies the request method, headers, cookies and a response channel for each request, while a CLI run receives only its own fixed inputs and exits.

## Reference comparison

Open `courses/web-development/solutions/web-031_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.

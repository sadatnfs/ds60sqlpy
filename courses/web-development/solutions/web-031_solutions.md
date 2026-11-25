# web-031: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-031.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict which characters in the greeting source appear in output.

**Expected answer:** The opening tag and echo keyword do not appear; the string content does.

**Approach:** Separate the PHP syntax from the data: the tag and the `echo` keyword are instructions, while the quoted string is what gets written.

**Why:** The `<?php` tag and `echo` are PHP syntax, so only the string's characters, including the newline written as `\n`, reach the output.

**Plausible wrong approach:** Expecting `<?php` to appear in the output fails because the interpreter consumes the opening tag and never prints it.

**How to verify:** Running the file in the CLI worker prints Hello, classroom. followed by a single newline and nothing else.

## Exercise 2: Change the planned minutes while preserving the label.

**Expected evidence:** Only the numeric portion changes.

**Approach:** Change only the value assigned to `$minutes` and leave the label string and the concatenation unchanged.

**Why:** The label is a separate string literal, so changing `$minutes` alters only the number that concatenation inserts.

**Plausible wrong approach:** Editing the number inside the label string fails because the variable still holds 30, so the printed value disagrees with the plan.

**How to verify:** After setting `$minutes = 45;`, the output reads Planned minutes: 45 with the label exactly as before.

## Exercise 3: Write a PHP program that prints a study topic and computed duration.

**Expected evidence:** The program runs in the CLI worker and produces two clearly labeled values.

**Approach:** Assign the topic and the session length to variables, compute the duration with an expression, and echo two labeled lines.

**Why:** Named values and one computation keep the program readable and let you verify the output by hand.

**Plausible wrong approach:** Printing the raw number without a label fails because a reader of the CLI output cannot tell which value is which.

**How to verify:** The worker output shows two lines, each beginning with its label, and the computed value matches a hand calculation.

## Exercise 4: Diagnose a missing semicolon as a parse error.

**Expected answer:** The interpreter cannot execute the intended statement sequence until syntax is repaired.

**Approach:** Read the line number in the parse error, look at the end of the previous statement, and add the missing semicolon.

**Why:** PHP parses the whole file before running it, so a syntax error stops execution and the reported line is often the one after the missing semicolon.

**Plausible wrong approach:** Searching the output for a partial result fails because a parse error stops the file before any statement runs at all.

**How to verify:** After adding the semicolon, the program runs and prints every line instead of a single parse error.

## Exercise 5: Print literal angle brackets and explain the output surface.

**Expected evidence:** The CLI displays text; it does not automatically render a web page.

**Approach:** Echo a string such as `<strong>` and note that the CLI worker prints characters to a text stream rather than rendering markup.

**Why:** The CLI writes plain text to standard output, so angle brackets are printed as characters; no browser parses them as HTML.

**Plausible wrong approach:** Expecting bold text in the CLI output fails because no browser parses the string, so the tags appear as plain characters.

**How to verify:** The worker output shows the literal text <strong> unchanged, with no change in font weight.

## Exercise 6: Compare the CLI lifecycle with a server request lifecycle.

**Expected answer:** A CLI process receives its prepared inputs; a server integration supplies HTTP context and response handling.

**Approach:** Describe where inputs come from in each case: prepared arguments for the CLI process, and request data plus headers for a server request.

**Why:** A server integration supplies the request method, headers, cookies and a response channel for each request, while a CLI run receives only its own fixed inputs and exits.

**Plausible wrong approach:** Assuming `$_GET` is filled when running the CLI worker fails because no HTTP request exists, so those arrays stay empty.

**How to verify:** Dumping `$_GET` in the CLI worker prints an empty array, while the program's prepared input values are present.

## Reference comparison

The reference checks that the computed minutes equal 30, then echoes the topic and minutes lines. That catches an arithmetic slip in the duration. It does not compare your label wording, test literal angle brackets or show a server lifecycle, so compare the printed lines with your own prediction.

Open `courses/web-development/solutions/web-031_solution.php` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).

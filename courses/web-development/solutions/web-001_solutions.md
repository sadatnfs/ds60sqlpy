# web-001: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-001.md`.

## Exercise 1: Predict which text from the first example is visible.

**Expected answer:** Only Hello, web. appears as paragraph text.

**Why:** Tags are instructions to the parser, not visible text, and the title is metadata shown in the tab; only character data inside body elements is painted.

## Exercise 2: Change a paragraph without changing the document title.

**Expected evidence:** The visible body changes while the browser document title remains the same.

**Why:** The title element and the body content are independent parts of the document tree, so editing a paragraph cannot change the tab text.

## Exercise 3: Build a complete document with a title, one heading and two paragraphs.

**Expected evidence:** The preview contains one main heading and two paragraphs inside the body.

**Why:** A complete document gives the parser an explicit standards mode, language, encoding and title, so the browser does not have to recover from missing structure.

## Exercise 4: Explain why PHP source pasted into an HTML page does not execute on a PHP server.

**Expected answer:** A browser preview parses HTML; no PHP interpreter or server request was involved.

**Why:** PHP runs only when a PHP interpreter processes the file, normally through a server. The HTML parser treats `<?php ... ?>` as a bogus comment, so nothing executes and the code is not even displayed.

## Exercise 5: Remove the styling and inspect what remains useful.

**Expected evidence:** Document structure and readable text remain; meaning does not depend on CSS.

**Why:** HTML elements carry meaning and order independently of CSS, so headings, paragraphs and links stay understandable when presentation is removed.

## Exercise 6: Trace a requested page from source to visible output.

**Expected answer:** Distinguish server response bytes, parsed document tree, applied style and painted output.

**Why:** Each stage can fail on its own: the server can send the wrong bytes, the parser can repair broken markup, CSS can hide content and painting can clip it, so naming the stage tells you where to look.

## Reference comparison

Open `courses/web-development/solutions/web-001_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.

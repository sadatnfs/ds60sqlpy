# web-001: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-001.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict which text from the first example is visible.

**Expected answer:** Only Hello, web. appears as paragraph text.

**Approach:** Read the example tag by tag and mark which characters are markup and which are character data inside the body.

**Why:** Tags are instructions to the parser, not visible text, and the title is metadata shown in the tab; only character data inside body elements is painted.

**Plausible wrong approach:** Counting the angle-bracket text as visible fails because `<p>` and `</p>` are consumed by the parser and never painted as letters.

**How to verify:** Open the preview and select all visible text; the copied text is exactly Hello, web. with no tag names.

## Exercise 2: Change a paragraph without changing the document title.

**Expected evidence:** The visible body changes while the browser document title remains the same.

**Approach:** Locate the `title` element in `head` and the paragraph in `body`, then edit only the paragraph's character data.

**Why:** The title element and the body content are independent parts of the document tree, so editing a paragraph cannot change the tab text.

**Plausible wrong approach:** Editing the `h1` and expecting the tab to follow fails because the tab label comes only from `title`, not from the first heading.

**How to verify:** After the edit, the browser tab or `document.title` in the console still shows the original title string.

## Exercise 3: Build a complete document with a title, one heading and two paragraphs.

**Expected evidence:** The preview contains one main heading and two paragraphs inside the body.

**Approach:** Type the skeleton first (doctype, `html lang`, `head` with `meta charset` and `title`, `body`), then add one `h1` and two `p` elements.

**Why:** A complete document gives the parser an explicit standards mode, language, encoding and title, so the browser does not have to recover from missing structure.

**Plausible wrong approach:** Leaving out the doctype still renders text, but the page drops into quirks mode, so later CSS box sizing lessons behave differently.

**How to verify:** In the console, `document.compatMode` returns CSS1Compat and `document.querySelectorAll('body p').length` returns 2.

## Exercise 4: Explain why PHP source pasted into an HTML page does not execute in the browser preview.

**Expected answer:** A browser preview parses HTML; no PHP interpreter or server request was involved.

**Approach:** Identify which program reads the file in this pad: the browser's HTML parser, which has no PHP interpreter attached.

**Why:** PHP runs only when a PHP interpreter processes the file, normally through a server. The HTML parser treats `<?php ... ?>` as a bogus comment, so nothing executes and the code is not even displayed.

**Plausible wrong approach:** Assuming the code ran silently with no output fails because the parser turns `<?php ... ?>` into a comment node and nothing executes.

**How to verify:** Inspect the Elements tree and find a comment node containing the PHP text, with no echoed output anywhere in the body.

## Exercise 5: Remove the styling and inspect what remains useful.

**Expected evidence:** Document structure and readable text remain; meaning does not depend on CSS.

**Approach:** Delete or comment out the `style` element, reload, and read the page from top to bottom as plain structure.

**Why:** HTML elements carry meaning and order independently of CSS, so headings, paragraphs and links stay understandable when presentation is removed.

**Plausible wrong approach:** Judging usefulness by how polished the page looks fails here, because the question is whether headings and paragraphs still order the content.

**How to verify:** With styles removed, the `h1` still appears first and both paragraphs follow in source order with default browser spacing.

## Exercise 6: Trace a requested page from source to visible output.

**Expected answer:** Distinguish server response bytes, parsed document tree, applied style and painted output.

**Approach:** Write four stages in order (bytes received, tree built, styles applied, pixels painted) and attach one possible failure to each.

**Why:** Each stage can fail on its own: the server can send the wrong bytes, the parser can repair broken markup, CSS can hide content and painting can clip it, so naming the stage tells you where to look.

**Plausible wrong approach:** Collapsing everything into the page loaded hides which stage failed, so a parser repair gets blamed on CSS or the server.

**How to verify:** For each stage, name the tool that shows it: Network panel for bytes, Elements for the tree, Computed for styles and the preview for paint.

## Reference comparison

The reference counts paragraphs inside main and requires exactly two, so it catches a missing or extra paragraph and a paragraph placed outside main. It does not read the title, check that the heading is an h1, or notice a misnested tag the parser silently repaired. Compare those parts by reading the rendered page and the Elements tree.

Open `courses/web-development/solutions/web-001_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).

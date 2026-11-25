# web-002: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-002.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Predict the text content after character references are parsed.

**Expected answer:** The browser displays comparison signs and an ampersand, not the entity source.

**Approach:** Replace each reference in the example with the character it names: `&lt;` becomes <, `&amp;` becomes & and `&gt;` becomes >.

**Why:** Character references are decoded during parsing, so the text node holds the real < and & characters while the source keeps them escaped.

**Plausible wrong approach:** Predicting that the reader sees `&lt;` literally fails because the parser decodes references in text before anything is painted.

**How to verify:** Run `document.querySelector('p').textContent` in the console and confirm it returns 2 < 3 & 3 > 2.

## Exercise 2: Add a language attribute and explain its role.

**Expected evidence:** The root lang attribute identifies the language for pronunciation and processing.

**Approach:** Put `lang="en"` on the `html` root so every descendant inherits the language unless an element overrides it.

**Why:** lang tells assistive technology which pronunciation rules to apply and lets browsers use language-specific hyphenation and quotation marks.

**Plausible wrong approach:** Putting `lang` only on one paragraph fails to describe the rest of the document, so screen readers may guess the language elsewhere.

**How to verify:** `document.documentElement.lang` returns en, and an inner element with `lang="fr"` reports its own value through `.lang`.

## Exercise 3: Build a notes paragraph with nested importance and literal angle brackets.

**Expected evidence:** The structure remains a paragraph and the comparison is text rather than an element.

**Approach:** Write a `p` containing a `strong` around the important word, and escape every literal angle bracket in the comparison text.

**Why:** Escaping keeps the comparison as text so the parser does not open a new element, while nested inline elements add importance without breaking the paragraph.

**Plausible wrong approach:** Typing a raw `<b` or `<x>` in the comparison fails because the parser starts a new element and the text after it vanishes from view.

**How to verify:** The Elements tree shows one `p` with one `strong` child and no unexpected element named after the comparison text.

## Exercise 4: Repair overlapping emphasis tags by drawing their tree.

**Expected evidence:** Each opened element is closed before its parent closes.

**Approach:** Draw the tree from the opening tags, then close the innermost open element before closing its parent.

**Why:** Elements form a tree, so a child must close before its parent closes. Crossing tags force the parser to repair the tree, which can split or extend the emphasis unexpectedly.

**Plausible wrong approach:** Swapping the closing tags so they overlap fails because the parser's adoption steps silently restructure the tree into something the source does not show.

**How to verify:** After repair, the Elements panel nesting matches your drawing exactly, with `strong` fully inside `em` or fully outside it.

## Exercise 5: Add two related notes without duplicating an id.

**Expected evidence:** Shared class names group them while each id remains unique.

**Approach:** Give both notes the same class for shared meaning and styling, and give each a different `id` only if something must target it.

**Why:** An id names one element for fragments, labels and scripts, so it must be unique; a class can mark any number of elements.

**Plausible wrong approach:** Reusing one `id` for both notes fails because `getElementById` and fragment links return only the first match, hiding the second note.

**How to verify:** `document.querySelectorAll('.note').length` returns 2 while each `id` you assigned appears exactly once in the tree.

## Exercise 6: Explain escaping versus validation with a text and URL example.

**Expected answer:** Escaping preserves literal text; URL validation separately restricts allowed schemes and destinations.

**Approach:** Escape the text example so it displays literally, then separately check the URL example's scheme against an allowlist such as https.

**Why:** Escaping changes how a value is written in one output context so it stays text; validation rejects values such as a javascript: URL that remain dangerous even when correctly escaped.

**Plausible wrong approach:** Escaping a `javascript:` URL fails as a defense because escaping only changes how characters print; the dangerous scheme is still a valid link target.

**How to verify:** The escaped text shows angle brackets as characters, and a `javascript:` URL is rejected by the scheme check rather than rendered as a link.

## Reference comparison

The reference reads the text content of the element with id note and requires the literal string 2 < 3 & 3 > 2, so it fails if a character reference was left raw and parsed as markup or if the comparison was retyped. It does not check the lang attribute, unique ids or whether importance uses strong rather than b.

Open `courses/web-development/solutions/web-002_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).

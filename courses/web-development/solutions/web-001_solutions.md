# web-001: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

HTML is a markup language: it names the structure and meaning of a document. CSS is a style language that controls how that structure is presented. JavaScript is a programming language executed by the browser or another host. PHP is a programming language commonly executed by a server. A visitor receives the server's response, not the PHP source that generated it. These layers can cooperate without becoming interchangeable.

A browser parses HTML into a document tree, applies style rules and paints pixels. A server accepts a request and returns a response. Opening a local preview exercises the browser portion; it does not demonstrate a network request, authentication or a server database. Our first document is deliberately small enough to inspect every character and every visible element.

An element such as `<p>Hello</p>` has an opening tag, content and a closing tag. The tag names the kind of content. A document begins with `<!doctype html>` to request standards rendering, then an `html` root containing `head` metadata and `body` visible content. The `title` labels the browser document, while an `h1` labels the visible topic. Whitespace in ordinary text is generally collapsed, so source indentation helps humans without creating layout.

## Exercise 1: Predict which text from the first example is visible.

Only Hello, web. appears as paragraph text.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Change a paragraph without changing the document title.

The visible body changes while the browser document title remains the same.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a complete document with a title, one heading and two paragraphs.

The preview contains one main heading and two paragraphs in a main region.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Explain why PHP source pasted into an HTML page does not execute on a PHP server.

A browser preview parses HTML; no PHP interpreter or server request was involved.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Remove the styling and inspect what remains useful.

Document structure and readable text remain; meaning does not depend on CSS.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Trace a requested page from source to visible output.

Distinguish server response bytes, parsed document tree, applied style and painted output.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

# web-006: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-006.md`.

## Exercise 1: Choose alternatives for decorative and informative images.

**Expected answer:** Decorative images have empty alternatives; informative ones convey task-relevant meaning.

**Why:** alt="" tells assistive technology to skip a decorative image, while an informative image needs text that delivers the same information.

## Exercise 2: Add a visible caption without repeating a verbose alternative.

**Expected evidence:** Caption and alternative serve complementary roles.

**Why:** figcaption is visible to all readers, while alt substitutes for the image; repeating the same text makes a screen reader announce it twice.

## Exercise 3: Create an offline SVG progress illustration with a textual equivalent.

**Expected evidence:** The image has an accessible name and the numeric progress is visible as text.

**Why:** An inline SVG needs a name, for example role="img" with aria-label or a title, to be announced as one image, and visible text keeps the value available to everyone.

## Exercise 4: Explain why chart alt text saying chart is insufficient.

**Expected answer:** It names the object but omits the information the reader needs.

**Why:** Alternative text should carry the purpose and key values, such as the trend or the largest category, not just the type of graphic.

## Exercise 5: Shrink the preview and preserve the SVG aspect ratio.

**Expected evidence:** The illustration scales while labels and the textual equivalent remain readable.

**Why:** The viewBox defines the internal coordinate system, so the drawing scales proportionally when only its rendered width changes.

## Exercise 6: Plan an accessible video lesson without autoplay.

**Expected evidence:** Provide controls, captions and a transcript, with deliberate download size and motion choices.

**Why:** Captions serve people who cannot hear, transcripts and descriptions serve people who cannot see or prefer text, and avoiding autoplay respects attention, motion sensitivity and data limits.

## Reference comparison

Open `courses/web-development/solutions/web-006_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.

# web-006: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-006.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Choose alternatives for decorative and informative images.

**Expected answer:** Decorative images have empty alternatives; informative ones convey task-relevant meaning.

**Approach:** For each image ask what the reader loses if it disappears; nothing means `alt=""`, and a task fact means alt text stating that fact.

**Why:** alt="" tells assistive technology to skip a decorative image, while an informative image needs text that delivers the same information.

**Plausible wrong approach:** Omitting `alt` entirely on a decorative image fails because some screen readers then announce the file name instead of skipping it.

**How to verify:** In the Elements panel, decorative images carry `alt=""` and the informative image's `alt` states the location fact.

## Exercise 2: Add a visible caption without repeating a verbose alternative.

**Expected evidence:** Caption and alternative serve complementary roles.

**Approach:** Wrap the image in `figure`, add a visible `figcaption`, and shorten `alt` so it does not repeat the caption word for word.

**Why:** figcaption is visible to all readers, while alt substitutes for the image; repeating the same text makes a screen reader announce it twice.

**Plausible wrong approach:** Copying the caption into `alt` fails because screen reader users hear the same sentence twice in a row.

**How to verify:** Read the `alt` value and the `figcaption` text side by side; they share no repeated sentence.

## Exercise 3: Create an offline SVG progress illustration with a textual equivalent.

**Expected evidence:** The image has an accessible name and the numeric progress is visible as text.

**Approach:** Draw the bar with inline SVG, set `role="img"` and `aria-labelledby` to a `title`, and print the numeric progress as visible text.

**Why:** An inline SVG needs a name, for example role="img" with aria-label or a title, to be announced as one image, and visible text keeps the value available to everyone.

**Plausible wrong approach:** Loading the illustration from a remote URL fails here because the offline preview blocks external assets and leaves an empty box.

**How to verify:** The accessibility panel shows an image named by the title, and the visible text shows the same count as the bar.

## Exercise 4: Explain why chart alt text saying chart is insufficient.

**Expected answer:** It names the object but omits the information the reader needs.

**Approach:** Compare what the alt text names with what a sighted reader learns, which is the values and the trend the chart shows.

**Why:** Alternative text should carry the purpose and key values, such as the trend or the largest category, not just the type of graphic.

**Plausible wrong approach:** Writing Bar chart of minutes fails because it names the kind of object but gives no number, comparison or conclusion.

**How to verify:** A replacement alt or nearby summary states at least one value and the main comparison a reader would take from the chart.

## Exercise 5: Shrink the preview and preserve the SVG aspect ratio.

**Expected evidence:** The illustration scales while labels and the textual equivalent remain readable.

**Approach:** Keep the `viewBox`, remove fixed pixel width, and let CSS set `width: 100%` with height following the aspect ratio.

**Why:** The viewBox defines the internal coordinate system, so the drawing scales proportionally when only its rendered width changes.

**Plausible wrong approach:** Setting both width and height in percentages fails because the drawing stretches and the bar proportions no longer match the data.

**How to verify:** At the narrow preset the SVG shrinks evenly, and its rendered width to height ratio still matches the 100 by 30 viewBox.

## Exercise 6: Plan an accessible video lesson without autoplay.

**Expected evidence:** Provide controls, captions and a transcript, with deliberate download size and motion choices.

**Approach:** Choose `controls` without `autoplay`, add a captions `track`, and link a transcript while stating the file size before download.

**Why:** Captions serve people who cannot hear, transcripts and descriptions serve people who cannot see or prefer text, and avoiding autoplay respects attention, motion sensitivity and data limits.

**Plausible wrong approach:** Relying on autoplay with muted sound fails because motion still starts without consent and captions alone do not replace a transcript.

**How to verify:** Your plan lists controls, captions, a transcript and a size note, with autoplay absent from the proposed element.

## Reference comparison

The reference reads the text of the SVG title and requires the word Three, so it fails if the title is missing or describes a different progress value. It does not prove the title is referenced by aria-labelledby, that decorative images have empty alt text or that the figure keeps its aspect ratio at narrow widths.

Open `courses/web-development/solutions/web-006_solution.html` after saving your attempt ([comparing with the reference](../STUDY-GUIDE.md#references)).

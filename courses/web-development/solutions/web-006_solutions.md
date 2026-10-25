# web-006: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Alternative text communicates an image's purpose in its context. A decorative image may use empty alt text so it does not add noise. An informative image needs a concise equivalent; a complex chart usually needs surrounding explanation or a data table as well. A filename is rarely useful alternative text. The same picture can need different alternatives in different contexts because the task differs.

A figure groups self-contained media with a caption. A caption is visible to everyone, while an alternative serves when the image is unavailable or not visually perceived. SVG describes vector geometry and can be written inline, which keeps our fixtures offline. A viewBox defines internal coordinates; CSS controls the displayed dimensions. Width and height reserve space and reduce unexpected layout movement.

For inline SVG, connect a title and description using `aria-labelledby`, and use `role="img"` for a meaningful standalone illustration. Decorative SVG can be hidden from assistive technology. Use a textual list when exact values matter. Audio and video require captions or transcripts, appropriate controls and deliberate autoplay decisions; no media downloads are required by this lesson.

## Exercise 1: Choose alternatives for decorative and informative images.

Decorative images have empty alternatives; informative ones convey task-relevant meaning.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a visible caption without repeating a verbose alternative.

Caption and alternative serve complementary roles.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Create an offline SVG progress illustration with a textual equivalent.

The image has an accessible name and the numeric progress is visible as text.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Explain why chart alt text saying chart is insufficient.

It names the object but omits the information the reader needs.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Shrink the preview and preserve the SVG aspect ratio.

The illustration scales while labels and the textual equivalent remain readable.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Plan an accessible video lesson without autoplay.

Provide controls, captions and a transcript, with deliberate download size and motion choices.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

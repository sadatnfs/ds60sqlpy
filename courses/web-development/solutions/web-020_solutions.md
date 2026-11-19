# web-020: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-020.md`.

## Exercise 1: Identify the difference between a transition and keyframe animation.

**Expected answer:** A transition follows a property change; an animation follows a named timeline.

**Why:** A transition interpolates between two values when a property changes, while @keyframes define a timeline that runs on its own.

## Exercise 2: Limit a transition to one intentional property.

**Expected evidence:** Unrelated style changes no longer animate automatically.

**Why:** transition: all animates every later property change, including ones you did not intend; listing one property keeps the effect deliberate.

## Exercise 3: Build a card interaction with a static reduced-motion alternative.

**Expected evidence:** The card remains understandable and usable without movement.

**Why:** The reduced-motion query lets people who are sensitive to motion get a fully usable static interaction.

## Exercise 4: Diagnose an animation that hides information until it finishes.

**Expected answer:** Make the essential content available without waiting for motion.

**Why:** Information that appears only at the end of an animation delays or hides it for everyone and fails when motion is disabled.

## Exercise 5: Test with reduced motion enabled and with keyboard focus.

**Expected evidence:** Motion is reduced and the focus indicator still communicates interaction.

**Why:** Disabling motion must not remove the focus indicator, which communicates state rather than decoration.

## Exercise 6: Explain why transform does not guarantee a fast page.

**Expected answer:** The full rendering workload, content size and device determine performance.

**Why:** transform avoids layout but still costs painting and compositing, so total workload and device speed decide performance.

## Reference comparison

Open `courses/web-development/solutions/web-020_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.

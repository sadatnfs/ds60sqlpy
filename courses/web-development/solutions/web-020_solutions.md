# web-020: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-020.md`.

## Exercise 1: Identify the difference between a transition and keyframe animation.

**Expected answer:** A transition follows a property change; an animation follows a named timeline.

**Approach:** Compare triggers: a transition runs only when a property value changes, while a keyframe animation runs from its own named timeline.

**Why:** A transition interpolates between two values when a property changes, while @keyframes define a timeline that runs on its own.

**Plausible wrong approach:** Expecting a transition to loop fails because it runs once per value change and stops at the new value.

**How to verify:** A hover transition plays once per hover and then rests, while an `animation` with `animation-iteration-count: infinite` keeps running with no interaction at all.

## Exercise 2: Limit a transition to one intentional property.

**Expected evidence:** Unrelated style changes no longer animate automatically.

**Approach:** Replace `transition: all` with `transition: transform 120ms ease` so only the intended movement animates.

**Why:** transition: all animates every later property change, including ones you did not intend; listing one property keeps the effect deliberate.

**Plausible wrong approach:** Keeping `all` with a shorter duration fails because unrelated layout changes still animate, just more quickly.

**How to verify:** Changing the card's padding in developer tools happens instantly while hover still animates the transform.

## Exercise 3: Build a card interaction with a static reduced-motion alternative.

**Expected evidence:** The card remains understandable and usable without movement.

**Approach:** Add the hover transform and a reduced-motion media query that removes both the transition and the transform.

**Why:** The reduced-motion query lets people who are sensitive to motion get a fully usable static interaction.

**Plausible wrong approach:** Removing only the transition fails because the card still jumps 2px on hover, which is still motion.

**How to verify:** With reduced motion emulated, hovering leaves the card in place and its border or outline still changes.

## Exercise 4: Diagnose an animation that hides information until it finishes.

**Expected answer:** Make the essential content available without waiting for motion.

**Approach:** Make the content visible in its final state by default and let motion only decorate that change.

**Why:** Information that appears only at the end of an animation delays or hides it for everyone and fails when motion is disabled.

**Plausible wrong approach:** Starting content at `opacity: 0` until an animation finishes fails because a failed or skipped animation leaves the text invisible.

**How to verify:** With animations disabled in developer tools, or with the keyframes rule deleted, all text is visible and readable as soon as the page loads.

## Exercise 5: Test with reduced motion enabled and with keyboard focus.

**Expected evidence:** Motion is reduced and the focus indicator still communicates interaction.

**Approach:** Emulate `prefers-reduced-motion: reduce`, then tab through the cards and confirm each focus outline is still visible.

**Why:** Disabling motion must not remove the focus indicator, which communicates state rather than decoration.

**Plausible wrong approach:** Disabling all hover and focus styles under reduced motion fails because users lose the focus signal along with the motion.

**How to verify:** With the preference on, no element moves and every focused card still shows its outline.

## Exercise 6: Explain why transform does not guarantee a fast page.

**Expected answer:** The full rendering workload, content size and device determine performance.

**Approach:** Profile a hover on a page with many large cards and look at layout, paint and composite work in the performance panel.

**Why:** transform avoids layout but still costs painting and compositing, so total workload and device speed decide performance.

**Plausible wrong approach:** Assuming transform is free fails because large layers, many elements and slow devices still cost memory and frame time.

**How to verify:** The performance trace shows frame timings for the hover on each version, and you compare those recorded numbers instead of assuming which one is faster.

## Reference comparison

Open `courses/web-development/solutions/web-020_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.

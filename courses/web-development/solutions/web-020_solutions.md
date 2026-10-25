# web-020: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Motion can explain a change, but it can also distract, delay a task or cause discomfort. A transition interpolates between property values when state changes. An animation uses named keyframes over time. Neither should be required to understand essential content. Begin with the static usable state and add restrained motion only when it improves orientation.

Animating layout-affecting properties can trigger repeated layout work, while transform and opacity often allow more efficient compositing. This is not a guarantee of smooth performance because element size, painting and the device still matter. Measure actual behavior rather than assuming that a property name proves efficiency. Continuous decorative motion rarely helps a reading task.

Specify the properties to transition instead of transition:all, which can animate unrelated future changes. The prefers-reduced-motion media query lets a page respond to a user's preference. A reduced-motion rule can remove movement while retaining a color or outline change. Do not use a tiny but nonzero duration as a universal accessibility strategy; understand the interaction's required events and states.

## Exercise 1: Identify the difference between a transition and keyframe animation.

A transition follows a property change; an animation follows a named timeline.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Limit a transition to one intentional property.

Unrelated style changes no longer animate automatically.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a card interaction with a static reduced-motion alternative.

The card remains understandable and usable without movement.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose an animation that hides information until it finishes.

Make the essential content available without waiting for motion.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test with reduced motion enabled and with keyboard focus.

Motion is reduced and the focus indicator still communicates interaction.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why transform does not guarantee a fast page.

The full rendering workload, content size and device determine performance.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

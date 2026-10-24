# js-055: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A transition changes attributes over time rather than setting the final state immediately. Interpolation computes intermediate values, while easing controls the pace along the timeline. Motion can help a reader follow identity through a change, but it can also distract, delay access or imply a continuous process that the data does not represent.

Transitions are asynchronous. Starting one does not mean its final geometry exists on the next line. A newer update may interrupt an earlier transition, so a component must decide whether to finish, replace or cancel work. Awaiting a transition’s completion can reject when it is interrupted; handling that rejection is part of lifecycle correctness.

Reduced-motion preferences should lead to a useful static or immediate update. Do not make animation the only way to discover a value or state change. The reference uses a short bounded transition, respects the media preference and checks the final state after completion.

Name transitions when a component needs a clear interruption channel. Call `.interrupt(name)` before replacing obsolete work. A named transition’s `.end()` returns a promise for completion. The final data state should be stored independently of a partly animated attribute.

For deterministic testing, assert the final value after awaiting the promise, not after guessing a sleep duration. Timing varies across machines and background tabs. The reference does not run an infinite animation loop.

## Exercise 1: Predict an attribute read immediately after starting a transition.

Starting asynchronous work is not completion. Wait on the operation that defines the intended boundary.

**Expected:** It can still be the initial or intermediate value.

## Exercise 2: Set duration to zero under reduced motion.

Accessibility should preserve information and control, not remove the update entirely.

**Expected:** The final value remains available without movement.

## Exercise 3: Implement a bounded transition with completion checks.

A guessed timeout can be flaky under load. Use the transition promise to synchronize with actual completion.

**Expected:** Final geometry is asserted only after the transition ends.

## Exercise 4: Diagnose a rejected end promise after a new update.

Interruption is a meaningful lifecycle result. Handle it intentionally instead of treating every rejection as a successful animation.

**Expected:** The earlier transition may have been interrupted.

## Exercise 5: Replace an obsolete transition by name.

Named ownership avoids canceling unrelated animations. Keep data state separate from whatever intermediate geometry was visible.

**Expected:** Only the component-owned update channel is interrupted.

## Exercise 6: Defend when to use a static update.

Animation is a design choice, not a requirement of a polished chart. Respect speed, attention and motion sensitivity.

**Expected:** Prefer immediate clarity when motion adds no explanatory value.

# js-055: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A transition changes attributes over time rather than setting the final state immediately. Interpolation computes intermediate values, while easing controls the pace along the timeline. Motion can help a reader follow identity through a change, but it can also distract, delay access or imply a continuous process that the data does not represent.

Transitions are asynchronous. Starting one does not mean its final geometry exists on the next line. A newer update may interrupt an earlier transition, so a component must decide whether to finish, replace or cancel work. Awaiting a transition’s completion can reject when it is interrupted; handling that rejection is part of lifecycle correctness.

Reduced-motion preferences should lead to a useful static or immediate update. Do not make animation the only way to discover a value or state change. The reference uses a short bounded transition, respects the media preference and checks the final state after completion.

Name transitions when a component needs a clear interruption channel. Call `.interrupt(name)` before replacing obsolete work. A named transition’s `.end()` returns a promise for completion. The final data state should be stored independently of a partly animated attribute.

For deterministic testing, assert the final value after awaiting the promise, not after guessing a sleep duration. Timing varies across machines and background tabs. The reference does not run an infinite animation loop.

## Exercise 1: Predict an attribute read immediately after starting a transition.

Starting asynchronous work is not completion. Wait on the operation that defines the intended boundary. Right after mark.transition("update").attr("cx", 480), reading mark.attr("cx") still returns 80 because the tween runs on later animation frames. Checking cx on the next line and seeing 80 is not a bug. The reference awaits .end() before asserting 480.

**Expected:** It can still be the initial or intermediate value.

## Exercise 2: Set duration to zero under reduced motion.

Accessibility should preserve information and control, not remove the update entirely. When matchMedia("(prefers-reduced-motion: reduce)") matches, the reference uses duration 0, so the circle jumps to 480 and the text says "Immediate update: reduced motion requested". Skipping the update entirely would leave the circle at 80 and hide the new state. Toggle the setting in DevTools rendering options and confirm cx is 480 either way.

**Expected:** The final value remains available without movement.

## Exercise 3: Implement a bounded transition with completion checks.

A guessed timeout can be flaky under load. Use the transition promise to synchronize with actual completion. The reference awaits mark.transition("update").duration(120).end() and only then checks cx === 480. A setTimeout of 120 milliseconds could fire before the last frame on a busy machine and make the check flaky. Run the lesson several times with CPU throttling to see the promise version stay green.

**Expected:** Final geometry is asserted only after the transition ends.

## Exercise 4: Diagnose a rejected end promise after a new update.

Interruption is a meaningful lifecycle result. Handle it intentionally instead of treating every rejection as a successful animation. Starting a second "update" transition before the first finishes rejects the first .end() promise. Catching it as an error report would be noise; treat it as superseded and only assert on the transition that last owns the channel.

**Expected:** The earlier transition may have been interrupted.

## Exercise 5: Replace an obsolete transition by name.

Named ownership avoids canceling unrelated animations. Keep data state separate from whatever intermediate geometry was visible. mark.interrupt("update") cancels only transitions named "update"; a separate "highlight" transition on the same circle keeps running. Calling mark.interrupt() without a name would stop both. Start both and check which reaches its end.

**Expected:** Only the component-owned update channel is interrupted.

## Exercise 6: Defend when to use a static update.

Animation is a design choice, not a requirement of a polished chart. Respect speed, attention and motion sensitivity. For a single value change from 80 to 480 with no ordering to follow, an instant update reads just as well; keep motion for changes whose path explains something.

**Expected:** Prefer immediate clarity when motion adds no explanatory value.

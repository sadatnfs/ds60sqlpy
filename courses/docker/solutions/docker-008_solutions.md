# docker-008: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-008.md`.

## Exercise 1: Distinguish Compose interpolation from container environment.

**Expected answer:** Model rendering versus process input.

**Why:** A value used to choose a host port need not appear inside the container. Conversely, a container environment entry can be literal and independent of a host variable.

## Exercise 2: Predict the type of APP_MESSAGE.

**Expected answer:** A string, even when its contents look numeric.

**Why:** Environment values do not carry a native integer or Boolean type. The application must parse and validate domain-specific meanings before using them.

## Exercise 3: Design defaults and validation for a timeout variable.

**Expected evidence:** A documented default plus finite positive bounded numeric parsing.

**Why:** Configuration is external input. Rejecting malformed or excessive values at startup gives a clearer failure than a later hang caused by an unintended timeout.

## Exercise 4: Diagnose an exec array containing literal $PORT.

**Expected answer:** No shell expansion occurs in an argument array.

**Why:** The runtime passes the characters directly. Add explicit application parsing rather than introducing a shell merely to conceal that the command contract was misunderstood.

## Exercise 5: Explain why restart may not apply changed Compose environment.

**Expected answer:** Existing container configuration and recreation differ.

**Why:** Restart starts the same configured object again. Applying a changed service model may require recreation, so confirm the observed environment and container identity.

## Exercise 6: Write a public configuration evidence record.

**Expected evidence:** Name, safe synthetic value, source of override and observed response.

**Why:** Evidence should prove the intended precedence without leaking secrets. A response demonstrating the public message connects model rendering to actual application behavior.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.

# docker-008: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Configuration changes behavior without rebuilding application logic. Environment variables are string values supplied to a process. Command arguments are an ordered array of strings. Image defaults, Compose interpolation and the container’s environment are related but distinct mechanisms.

A Compose `.env` file commonly supplies values used when Compose renders its model. That does not mean every value is automatically injected into every container. A service’s `environment` or `env_file` configuration controls injection. Host-shell interpolation, Compose interpolation and shell expansion inside a container occur at different times.

Treat configuration as data with validation. A missing value should produce a clear startup error or documented default. A string containing `false` is still a nonempty string in many languages. Numeric ports and timeouts need parsing and bounds. Secrets should not be casually placed in versioned files or printed by a diagnostic command.

The fixture reads `APP_MESSAGE` and serves it in a JSON field. Compose explicitly sets the value. A source-only message edit changes the image; an environment edit changes runtime configuration and usually requires container recreation to take effect. An image environment value is a default which runtime options can override.

The exec-form command array does not expand `$NAME` like a shell. If the application needs an environment value, have the application read it or use an intentionally reviewed shell wrapper. `docker compose config` is valuable for validation but can display interpolated private values; use synthetic data in this lesson.

## Exercise 1: Distinguish Compose interpolation from container environment.

A value used to choose a host port need not appear inside the container. Conversely, a container environment entry can be literal and independent of a host variable.

**Expected:** Model rendering versus process input.

## Exercise 2: Predict the type of APP_MESSAGE.

Environment values do not carry a native integer or Boolean type. The application must parse and validate domain-specific meanings before using them.

**Expected:** A string, even when its contents look numeric.

## Exercise 3: Design defaults and validation for a timeout variable.

Configuration is external input. Rejecting malformed or excessive values at startup gives a clearer failure than a later hang caused by an unintended timeout.

**Expected:** A documented default plus finite positive bounded numeric parsing.

## Exercise 4: Diagnose an exec array containing literal $PORT.

The runtime passes the characters directly. Add explicit application parsing rather than introducing a shell merely to conceal that the command contract was misunderstood.

**Expected:** No shell expansion occurs in an argument array.

## Exercise 5: Explain why restart may not apply changed Compose environment.

Restart starts the same configured object again. Applying a changed service model may require recreation, so confirm the observed environment and container identity.

**Expected:** Existing container configuration and recreation differ.

## Exercise 6: Write a public configuration evidence record.

Evidence should prove the intended precedence without leaking secrets. A response demonstrating the public message connects model rendering to actual application behavior.

**Expected:** Name, safe synthetic value, source of override and observed response.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.

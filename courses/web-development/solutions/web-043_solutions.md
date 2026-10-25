# web-043: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An instant identifies a point on the timeline. A local date and time require a time zone and can be ambiguous or nonexistent around daylight-saving transitions. A fixed offset such as +00:00 is not the same as a named region with changing rules. Store and communicate the representation deliberately instead of assuming every day has exactly twenty-four local hours.

DateTimeImmutable returns a new object when modified, which reduces accidental changes to a shared value. Deterministic tests use a fixed clock or an injected instant rather than the current wall time. Otherwise a test can change result at midnight or fail only in another developer's time zone. User-facing formatting belongs at the presentation boundary.

Parse a documented ISO-like timestamp with an explicit offset for the basic example. Convert to another zone for display without changing the represented instant. A duration measured in elapsed seconds differs from a calendar operation such as next day in a region. Validate parsing failures and inspect warnings when accepting externally formatted dates.

## Exercise 1: Explain an instant versus a local clock reading.

An instant is a timeline point; a local reading needs zone context and can be ambiguous.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Convert a fixed instant to a named time zone.

The displayed hour changes but the Unix timestamp remains equal.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a deterministic study-session time report.

The output uses explicit time zones and a fixed input suitable for repeatable tests.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a test that fails around midnight.

Replace ambient current time with a controlled clock or input.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Compare elapsed seconds with a calendar-day operation near a clock change.

They can represent different elapsed durations; document which the application intends.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why a numeric offset is not a complete regional time-zone rule.

A region can change offsets over time due to daylight saving or policy changes.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

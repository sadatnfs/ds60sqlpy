# docker-010: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-010.md`.

## Exercise 1: Predict the streams used by the two short programs.

**Expected answer:** Success line on stdout, failure diagnostic on stderr.

**Why:** Stream conventions help tools separate normal output from diagnostics. They do not prevent an application from misusing a stream, so inspect its documented behavior.

## Exercise 2: Choose a bounded log command.

**Expected answer:** Project-scoped service logs with an explicit tail limit.

**Why:** A bounded sample is easier to review and less likely to leak unrelated data. Scope should be enforced by project and service selection rather than by filtering a huge global dump afterward.

## Exercise 3: Write an incident observation packet.

**Expected evidence:** Image identity, lifecycle state, recent logs and one failing request.

**Why:** These observations connect source packaging to the process and application layers. Include timestamps so a later healthy state is not confused with the original failure.

## Exercise 4: Diagnose a running container that returns errors.

**Expected answer:** Investigate application behavior rather than declaring success from running.

**Why:** The engine reports process lifecycle. HTTP responses and domain assertions establish whether that process performs its intended function.

## Exercise 5: Explain why a restart-only repair is weak evidence.

**Expected answer:** It can hide the cause and may not preserve a useful failure record.

**Why:** A restart can be an operational mitigation while still leaving root cause unknown. State both facts instead of claiming that disappearance proves a permanent fix.

## Exercise 6: Design log content for a public teaching server.

**Expected evidence:** Useful request metadata without tokens, raw secrets or private payloads.

**Why:** Logs often persist beyond the request. A small diagnostic schema gives enough context to debug while limiting the information copied into reports or shared screenshots.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.

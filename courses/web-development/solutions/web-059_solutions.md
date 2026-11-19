# web-059: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-059.md`.

## Exercise 1: Explain why PHP-FPM is not interchangeable with the development HTTP server.

**Expected answer:** FPM manages FastCGI workers and needs an appropriate HTTP-facing integration.

**Why:** PHP-FPM speaks FastCGI and needs a web server such as nginx in front of it, while the development server is single-process and not built for production.

## Exercise 2: Draw the public document root and private application directories.

**Expected answer:** Only intended static assets and entrypoints are directly served.

**Why:** Only the public document root with entrypoints and static assets should be reachable; source, configuration and secrets stay outside it.

## Exercise 3: Design a release plan for the study planner with durable storage.

**Expected evidence:** The plan covers configuration, secrets, migration, health, write/read acceptance, backup and rollback.

**Why:** Configuration, secrets, migrations, health, write and read checks, backups and rollback each need explicit evidence.

## Exercise 4: Diagnose secrets copied into an image layer.

**Expected answer:** Removing them in a later layer does not reliably erase earlier layer content; rotate exposed secrets and rebuild correctly.

**Why:** Every layer stays in the image, so a later deletion still ships the secret; rotate it and pass secrets at build time with a secret mount.

## Exercise 5: Describe a restore test in a separate disposable environment.

**Expected answer:** Recovered data and application behavior must be checked without overwriting the active store.

**Why:** Restoring into the active store risks overwriting good data, while a separate environment proves the backup is usable.

## Exercise 6: Explain what evidence is needed before publishing an image as ready.

**Expected answer:** Source, dependency, runtime, browser, data recovery and target-environment checks need explicit results and limits.

**Why:** A ready claim needs results for source, dependencies, runtime, browser, recovery and the target platform, plus stated limits.

## Comparing your worksheet

This lesson has no executable reference. Compare your worksheet with the answers above. The optional lab in `courses/web-development/fixtures/php-http-lab/` gives real request evidence only when you deliberately run it.

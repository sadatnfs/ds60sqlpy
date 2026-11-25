# web-059: explanatory solutions

Attempt each exercise before reading; the mechanism is in `courses/web-development/guides/web-059.md` ([using these answers](../STUDY-GUIDE.md#solutions)).

## Exercise 1: Explain why PHP-FPM is not interchangeable with the development HTTP server.

**Expected answer:** FPM manages FastCGI workers and needs an appropriate HTTP-facing integration.

**Approach:** Describe the development server as one process that answers HTTP directly, and FPM as a pool of workers that speak FastCGI to a web server in front.

**Why:** PHP-FPM speaks FastCGI and needs a web server such as nginx in front of it, while the development server is single-process and not built for production.

**Plausible wrong approach:** Pointing a browser at the FPM port fails because FPM expects FastCGI messages from a web server, not plain HTTP.

**How to verify:** Your diagram shows a reverse proxy between the browser and FPM, with FastCGI on that link.

## Exercise 2: Draw the public document root and private application directories.

**Expected answer:** Only intended static assets and entrypoints are directly served.

**Approach:** Draw a public folder holding index.php and static assets, and private folders for source, configuration, storage and vendor code.

**Why:** Only the public document root with entrypoints and static assets should be reachable; source, configuration and secrets stay outside it.

**Plausible wrong approach:** Serving the project root and blocking a few folders by rule fails because any forgotten file becomes downloadable.

**How to verify:** Your drawing sets the document root to public, with no secrets or source files inside it.

## Exercise 3: Design a release plan for the study planner with durable storage.

**Expected evidence:** The plan covers configuration, secrets, migration, health, write/read acceptance, backup and rollback.

**Approach:** Order the release steps: build the image, run migrations, check health, check a write and read, confirm backups, and rehearse rollback.

**Why:** Configuration, secrets, migrations, health, write and read checks, backups and rollback each need explicit evidence.

**Plausible wrong approach:** Treating a passing health check as release acceptance fails because health shows only that the process answered.

**How to verify:** Each step in your plan names its evidence, such as a stored synthetic plan read back after the release.

## Exercise 4: Diagnose secrets copied into an image layer.

**Expected answer:** Removing them in a later layer does not reliably erase earlier layer content; rotate exposed secrets and rebuild correctly.

**Approach:** Rotate the exposed secret first, then remove it from the build and supply it at container start instead.

**Why:** Every layer stays in the image, so a later deletion still ships the secret; rotate it and pass secrets at build time with a secret mount.

**Plausible wrong approach:** Adding a `RUN rm` line and pushing a new tag fails because the old layer stays in the registry and in pulled copies.

**How to verify:** Inspecting the new image history shows no COPY of a secret file, and the old credential no longer works.

## Exercise 5: Describe a restore test in a separate disposable environment.

**Expected answer:** Recovered data and application behavior must be checked without overwriting the active store.

**Approach:** Restore the latest backup into a fresh disposable database and run the app against it, leaving the live store untouched.

**Why:** Restoring into the active store risks overwriting good data, while a separate environment proves the backup is usable.

**Plausible wrong approach:** Restoring over the live database to test the backup fails because a bad backup would then destroy real data.

**How to verify:** A known synthetic plan from before the backup appears in the restored copy and the live database is unchanged.

## Exercise 6: Explain what evidence is needed before publishing an image as ready.

**Expected answer:** Source, dependency, runtime, browser, data recovery and target-environment checks need explicit results and limits.

**Approach:** List the evidence a release needs: dependency review, image scan, runtime checks, browser tests, restore results and target checks.

**Why:** A ready claim needs results for source, dependencies, runtime, browser, recovery and the target platform, plus stated limits.

**Plausible wrong approach:** Publishing because the image built and the container started fails because neither step tests the application's behavior.

**How to verify:** Your checklist names a result and a limit for each item, including anything not yet tested.

## Comparing your worksheet

Compare your release plan with the solution's acceptance record and check that every claim names its evidence, such as a build log, a health check or a restore. Nothing in this lesson publishes or deploys, so mark any step you have not actually observed as planned rather than done.

This lesson has no executable reference ([worksheet rules](../STUDY-GUIDE.md#worksheets)).

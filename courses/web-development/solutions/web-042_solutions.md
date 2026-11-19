# web-042: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-042.md`.

## Exercise 1: Explain what a namespace does and does not install.

**Expected answer:** It groups names; it does not fetch code or create an autoloader by itself.

**Why:** A namespace only qualifies names; loading the file requires an include or an autoloader, and dependencies come from a package manager.

## Exercise 2: Compare a short imported name with its fully qualified name.

**Expected answer:** Both can refer to the same class when the import is explicit.

**Why:** A use statement creates an alias, so the short name and the fully qualified name refer to the same class.

## Exercise 3: Design a small project layout with source, tests and a public entrypoint.

**Expected evidence:** Application code and tests stay separate from the server's public document root.

**Why:** The web server serves only the public directory, so source, tests and dependency metadata are not downloadable.

## Exercise 4: Diagnose a missing class despite a correct namespace declaration.

**Expected answer:** Check source availability and autoload configuration separately from naming.

**Why:** A correct namespace does not load code; PSR-4 maps the namespace prefix to a directory, and the autoloader must be registered.

## Exercise 5: Explain why an untrusted include filename is dangerous.

**Expected answer:** It can cause unintended code to be loaded or executed outside the reviewed project.

**Why:** An attacker-controlled include can load unexpected files or execute uploaded code, so include paths must be fixed in code.

## Exercise 6: Describe a deliberate dependency update and lockfile review.

**Expected answer:** Resolve changes explicitly, review packages and licenses, test the result and deploy the recorded set.

**Why:** Review the lockfile diff, check package sources and licenses, run the tests and deploy the exact locked set.

## Reference comparison

Open `courses/web-development/solutions/web-042_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.

# web-042: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-042.md`.

## Exercise 1: Explain what a namespace does and does not install.

**Expected answer:** It groups names; it does not fetch code or create an autoloader by itself.

**Approach:** Separate naming from loading: a namespace prefixes class names, while files reach the process only through `require`, `include` or an autoloader.

**Why:** A namespace only qualifies names; loading the file requires an include or an autoloader, and dependencies come from a package manager.

**Plausible wrong approach:** Expecting `namespace Learning;` to download or find code fails because the declaration only changes how names inside the file are qualified.

**How to verify:** Referencing a class from a namespace whose file was never loaded raises a class not found Error.

## Exercise 2: Compare a short imported name with its fully qualified name.

**Expected answer:** Both can refer to the same class when the import is explicit.

**Approach:** Write `use Learning\Label;` at the top, then call `Label::text()` and compare it with `\Learning\Label::text()`.

**Why:** A use statement creates an alias, so the short name and the fully qualified name refer to the same class.

**Plausible wrong approach:** Calling `Label::text()` without the import inside another namespace fails because PHP resolves the short name relative to the current namespace.

**How to verify:** Both calls print Study, and `Label::class` prints the full name Learning\Label.

## Exercise 3: Design a small project layout with source, tests and a public entrypoint.

**Expected evidence:** Application code and tests stay separate from the server's public document root.

**Approach:** Put classes in src, tests in tests and only an index.php in public, and point the server's document root at public.

**Why:** The web server serves only the public directory, so source, tests and dependency metadata are not downloadable.

**Plausible wrong approach:** Using the project root as document root fails because files such as composer.json and src classes become directly downloadable.

**How to verify:** Your layout lists public as the only web-served folder, and no source or test file sits inside it.

## Exercise 4: Diagnose a missing class despite a correct namespace declaration.

**Expected answer:** Check source availability and autoload configuration separately from naming.

**Approach:** Check that the class file exists, that the PSR-4 prefix maps to the right folder, and that the autoloader was regenerated.

**Why:** A correct namespace does not load code; PSR-4 maps the namespace prefix to a directory, and the autoloader must be registered.

**Plausible wrong approach:** Rewriting the namespace line repeatedly fails when the real cause is a missing file or a stale autoloader map.

**How to verify:** After fixing the mapping, `class_exists('Learning\Label')` returns true without any manual include.

## Exercise 5: Explain why an untrusted include filename is dangerous.

**Expected answer:** It can cause unintended code to be loaded or executed outside the reviewed project.

**Approach:** Trace how a page name becomes a file path and note that `../` segments let the path leave the intended folder.

**Why:** An attacker-controlled include can load unexpected files or execute uploaded code, so include paths must be fixed in code.

**Plausible wrong approach:** Stripping only the .php suffix from the input fails because the traversal segments and the include call are both untouched.

**How to verify:** Your explanation shows a concrete traversal value and the allowlist that rejects it.

## Exercise 6: Describe a deliberate dependency update and lockfile review.

**Expected answer:** Resolve changes explicitly, review packages and licenses, test the result and deploy the recorded set.

**Approach:** Run the update in a branch, read the lockfile diff for new or changed packages, run the tests, then commit the lockfile with the change.

**Why:** Review the lockfile diff, check package sources and licenses, run the tests and deploy the exact locked set.

**Plausible wrong approach:** Running an update directly on the production server fails because the installed set is never reviewed or reproducible.

**How to verify:** The commit contains the lockfile diff, the test run result and a note for each new package.

## Reference comparison

Open `courses/web-development/solutions/web-042_solution.php` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; server lifecycle, persistence, concurrency and security need their own integration evidence.

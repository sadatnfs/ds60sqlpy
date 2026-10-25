# web-042: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A namespace groups names so two libraries can use similar class names without colliding. It is a naming mechanism, not a directory, a security sandbox or an automatic package installer. Autoloading is a separate mechanism that resolves a class name to source when needed. Composer commonly manages package dependencies and generates an autoloader for a project.

A dependency manifest describes requirements, while a lockfile records a resolved dependency set. Reproducible deployment uses the reviewed lockfile and installed artifacts, with an explicit update process for security and compatibility. Opening a lesson must not download packages. The classroom single-file PHP worker has no arbitrary Composer project support, so the runnable example demonstrates namespaces in one file and the project workflow remains an external design.

PHP namespace declarations have placement rules. A bracketed namespace block can coexist with an explicitly bracketed global namespace in a single-file teaching program. Production projects should use a coherent autoloading convention rather than a manual chain of untrusted includes. A user-controlled include path can become code execution, so package and file resolution belong to reviewed application code.

## Exercise 1: Explain what a namespace does and does not install.

It groups names; it does not fetch code or create an autoloader by itself.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Compare a short imported name with its fully qualified name.

Both can refer to the same class when the import is explicit.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Design a small project layout with source, tests and a public entrypoint.

Application code and tests stay separate from the server's public document root.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a missing class despite a correct namespace declaration.

Check source availability and autoload configuration separately from naming.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Explain why an untrusted include filename is dangerous.

It can cause unintended code to be loaded or executed outside the reviewed project.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Describe a deliberate dependency update and lockfile review.

Resolve changes explicitly, review packages and licenses, test the result and deploy the recorded set.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

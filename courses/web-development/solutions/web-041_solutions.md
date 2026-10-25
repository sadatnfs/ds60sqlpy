# web-041: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An interface describes operations a caller can rely on without selecting a specific implementation. Composition builds behavior from collaborating objects. Dependency injection means supplying a dependency rather than constructing an unknown global dependency inside the operation. These techniques help when a real boundary varies, such as storage or time, but unnecessary interfaces can add ceremony to a tiny fixed calculation.

A test double supplies a controlled implementation for a test. An in-memory repository can verify application behavior without a database, but it does not prove SQL syntax, transactions or connection recovery. Keep unit evidence separate from integration evidence. The same interface can make both tests possible without pretending they are identical.

Define a repository interface with a narrow operation such as countCompleted. The service receives that interface through its constructor. A memory implementation holds synthetic records for this lesson. The service can then be tested with known data and no network. Later PDO lessons qualify the database boundary separately.

## Exercise 1: Identify the dependency hidden by the interface.

The application depends on progress-reading behavior, not a specific database implementation.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Supply an in-memory store with a known count.

The service output is deterministic and requires no external connection.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a summary service with an injected repository.

The same service works with two controlled implementations that satisfy the interface.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a test double that returns impossible domain values.

The double should preserve the relevant contract instead of making invalid states look normal.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test zero completed lessons.

The summary handles an empty state without a special external dependency.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain what remains untested by an in-memory repository.

Database queries, schema constraints, transactions and connection behavior require integration tests.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

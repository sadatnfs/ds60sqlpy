# web-050: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Passwords should not be stored as plaintext or encrypted with a reversible key merely so the application can compare them. A password hash is designed to make verification possible without retaining the original password and to impose a computational cost on guessing. Use a maintained password-hashing API rather than inventing a hash-plus-salt scheme. The encoded result records the algorithm and parameters needed for verification.

Authentication establishes an identity claim; it does not decide which objects that identity may access. A complete login flow also needs transport security, rate limiting, useful but nonrevealing errors, session rotation and account-recovery design. One successful hash comparison is only a primitive test, not a complete authentication system.

Use password_hash and password_verify. Allow storage large enough for future encoded formats, and use password_needs_rehash during a deliberate migration policy. Algorithm support and cost depend on the prepared runtime; the example uses bcrypt with an explicit bounded teaching cost. Production parameters require current guidance and measurement. Bcrypt has a byte-length limit that must not be ignored when designing input policy.

## Exercise 1: Explain hashing versus reversible encryption for passwords.

A password verifier needs a one-way verification representation, not recovery of the original secret.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Verify both a correct and incorrect synthetic phrase.

The library accepts only the correct candidate.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a password-verification demonstration without printing the hash or secret.

The output reports the test result while keeping credential-shaped values out of logs.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose using a general fast hash such as SHA-256 for password storage.

Fast general hashes do not provide a suitable password-guessing cost by themselves.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Explain an algorithm-specific input-length boundary.

The application must account for byte limits such as bcrypt's limit and avoid silent truncation policies.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: List the additional controls required around a real login.

TLS, rate limits, session rotation, recovery, safe errors and authorization remain separate requirements.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

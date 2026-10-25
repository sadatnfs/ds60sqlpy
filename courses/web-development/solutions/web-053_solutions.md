# web-053: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Authentication answers who the application believes is making a request. Authorization answers whether that identity may perform this action on this object. A record id in a URL is a locator, not proof of permission. A hidden owner field, disabled button or filtered interface cannot enforce access because the client can alter all of them.

Apply authorization on every relevant server operation, including reads, updates, deletion and exports. Scope queries by trusted identity or enforce an explicit policy before returning data. Deny by default when a required identity or permission is missing. Error behavior should avoid disclosing another user's sensitive record while still providing useful recovery for legitimate users.

The reference receives a trusted synthetic actor id as a separate parameter from the requested record id. A query includes both record id and owner id as bound values. The fake actor is a test fixture, not a login implementation. A real adapter must obtain it from a verified session or credential and must not copy it from a form field.

## Exercise 1: Explain why knowing a record id is not sufficient permission.

Ids identify objects; a policy must authorize access for the current actor.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add owner scoping to a prepared read query.

The query can return only the requested actor's matching record.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build an object-access function with separate trusted actor and requested id inputs.

The owner can read the record and a different actor receives no record.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose trusting owner_id from a submitted form.

A caller can forge it; derive ownership from the verified server-side identity.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test own, other and missing records.

Each follows a deliberate policy without leaking another actor's title.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why hiding an edit button is only a user-interface convenience.

The server endpoint must enforce the same permission even when called directly.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

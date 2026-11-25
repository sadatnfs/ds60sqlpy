"""Lesson-specific teaching text for go-043 to go-048 (see teaching.py)."""

PART6 = {
    "go-043": dict(
        predict="Predict finalAction for each state: a live object without the finalizer, a live object with it, a deleting object with cleanup outstanding, one with cleanup confirmed and one whose UID no longer matches. Decide why the ownership test comes first. Then predict which entries survive when only the lesson finalizer is removed.",
        pitfall="Removing the finalizer before cleanup succeeds is the orphaning bug: the API object disappears and nothing remembers the external resource. The opposite bug, never removing it, leaves the object stuck terminating. Remove only your own finalizer, never the whole list, and confirm the object is the incarnation you own; a recreated object with the same name has a different UID.",
        retrieval="Write `nextFinalizerStep(obj Object, cleanup func() error) (string, error)` that adds the finalizer to live objects, runs cleanup for deleting ones and removes only its own entry after success. Test cleanup that succeeds, fails and is already done, plus a list holding a foreign finalizer. Then explain what happens to the object if cleanup keeps failing.",
        hints=(
            "A live object without the finalizer needs registration. Which branch runs?",
            "The object is not deleting and the finalizer is present. What is the normal action?",
            "Deleting with cleanup outstanding. Which step must come before release?",
            "Cleanup is confirmed. What may the controller remove now?",
            "The ownership test runs before every other branch. What does a UID mismatch return?",
            "The filter skips one exact string. Which entry stays?",
        ),
        steps=(
            'With deleting set to true and no finalizer, finalAction returns done, so `=="add-finalizer"` fails. The function is right; the edited state describes a deleting object.',
            'A deleting object with cleanup pending returns cleanup, so `=="reconcile"` fails. Restore deleting to false for the healthy case.',
        ),
    ),
    "go-044": dict(
        predict="Predict which requests the local rule model admits: get on pods in lesson, delete under a get-only rule, get in another namespace, update on deployments when only deployments/status is granted, get on secrets under a pods rule, and watch when only list is granted. For each rejection, decide what it protects.",
        pitfall="Granting a controller cluster-admin, or the verb * on all resources, to make an error go away is the usual mistake; a bug or a stolen token then has unlimited reach. Grant the exact verbs, resources and namespace the code uses. Remember that list on secrets reveals their contents, watch is separate from list, and a status subresource grant does not permit spec updates.",
        retrieval="Write a Rule set for a controller that reads pods, lists and watches its own custom resource and updates only that resource's status in one namespace. Test each needed request and three refused ones: deleting pods, reading secrets and updating the main resource. Then explain the difference between authentication and authorization using a ServiceAccount token.",
        transfer="When a client-go call returns forbidden, read the error: it names the user, verb, resource and namespace, which maps directly onto a missing rule. Use kubectl auth can-i with --as to test a ServiceAccount before deploying. Review RBAC in the same pull request as the code that needs it, so authority grows only with a stated reason.",
        hints=(
            "Namespace, resource and verb all match. Is get listed?",
            "The rule lists only get. Is delete among its verbs?",
            "The rule names lesson. Does it match another namespace?",
            "deployments/status and deployments are different resources. Which request matches?",
            "The rule covers pods only. Does secrets match it?",
            "Only list is granted. Does watch match it?",
        ),
        steps=(
            "The rule now names namespace lesson!, so a request in lesson matches nothing and the read is refused. The model is right; the grant names the wrong namespace.",
            "delete is not granted, so allowed returns false and the check without negation fails. Restore `!` so the test asserts refusal.",
        ),
    ),
    "go-045": dict(
        predict="Predict the holder and expiry after a acquires an empty lease at time 10 for five units. Predict whether b can take a lease held by a at time 12, whether a can renew at 13 and whether b can take over at exactly 15. Then predict which fencing token the destination accepts and what a zero duration does.",
        pitfall="Treating leadership as exclusive is the dangerous assumption: a leader that pauses past its lease, for garbage collection or a network stall, wakes up still believing it leads while another replica acts. Leases reduce overlap but cannot prevent it. Protect external side effects with fencing tokens or idempotent writes, and stop work promptly when renewal fails.",
        retrieval="Write a lease simulation with acquire and a store that accepts writes only with the current fencing token, which increments on each takeover. Simulate a paused leader a, a takeover by b and a late write from a, and check that the store rejects it. Then explain why the lease alone would have let both writes through.",
        hints=(
            "The lease is empty. What do Holder and Expires become?",
            "a holds the lease until 15. Can b acquire at 12?",
            "The holder may renew early. What is the new expiry?",
            "The lease protects its holder only while now is below Expires. Can b acquire at 15?",
            "The destination accepts only the current token. Which of 4 and 5 passes?",
            "A nonpositive duration is refused first. Does the holder change?",
        ),
        steps=(
            "Acquiring at 11 sets Expires to 16, so `l.Expires==15` fails while the holder is still a. The acquisition works; the start time changed.",
            'The lease holder is now a!, so b is still refused but `l.Holder=="a"` fails. Restore the holder name a.',
        ),
    ),
    "go-046": dict(
        predict="Predict the decision for 3 replicas under a maximum of 5, for -1, and for exactly 5 and 6. Predict the UID copied into the response, and the SideEffects counter in dry-run and real mode. Then predict the decision for a request without a UID, and decide why the reason field matters to the person whose write was denied.",
        pitfall="A webhook that fails closed and then goes down blocks every write it covers, sometimes including the writes needed to repair it; one that fails open silently admits unchecked objects. Choose failurePolicy per webhook deliberately, scope it with selectors and keep its timeout short. A webhook with side effects must honor dryRun, and its response must echo the request UID.",
        retrieval="Write `validateLabels(uid string, labels map[string]string, dryRun bool) Decision` that requires an owner label, denies with a clear reason otherwise, echoes the UID and records a side effect only outside dry-run mode. Test allow, deny, missing UID and dry run. Then argue whether this webhook should fail open or closed, and why.",
        transfer="Admission sits between authorization and storage, so policy engines, defaulting webhooks and validating admission policies all follow this contract. When a deploy fails with a denied request, the reason should name the field and rule. When you write one, test boundaries, dry run and the unavailable case, and measure latency, because it sits on every write path it covers.",
        hints=(
            "3 lies within 0 to 5. What are Allowed and UID?",
            "-1 is outside the range. Which reason is set?",
            "The maximum itself is allowed. Is 6 within range?",
            "The decision starts from the request UID. What does the response carry?",
            "dryRun skips the counter. What do the two SideEffects values show?",
            "An empty UID is refused before range checks. Is the request allowed?",
        ),
        steps=(
            'The request UID is now r2, so the decision echoes r2 and `d.UID=="r1"` fails. Admission still allows the request; the identity changed.',
            'A denied decision carries a reason, so `d.Reason==""` is false and the check fails. Restore `!=""` so the test requires an explanation.',
        ),
    ),
    "go-047": dict(
        predict="Predict the value and call count when the fake reader returns 3, and when it returns ErrForbidden. For a canceled context, predict whether the fake is called at all. Predict whether a zero value is treated as failure, and whether a wrapped unknown error stays visible to errors.Is. Then decide what the receipt digest proves.",
        pitfall="Trusting fake-client tests as cluster evidence is the main error: a fake accepts objects a real API server would reject, never applies defaults or admission and returns no conflicts unless told to. Use fakes for decision logic and error paths, envtest or an API server for contracts, and an owned disposable cluster for end-to-end behavior. Count calls to catch hidden retries.",
        retrieval="Write a fake writer that fails with a conflict on its first call and succeeds on the second, and test a retrying caller against it by counting calls and checking the final value. Add a case where the context is canceled before the retry. Then list which behaviors of a real API server your fake cannot show, and which test layer would.",
        transfer="Every controller you build after this should carry three test layers: pure decision tests like plan and finalAction, fake-client tests for error handling and call counts, and an integration run against an owned cluster or envtest. Tie each piece of evidence to the exact source revision it tested, so a passing result is never reused for changed code.",
        hints=(
            "readOnce calls the fake once. What do v and Calls hold?",
            "The error is wrapped with %w. Can errors.Is still find ErrForbidden?",
            "readOnce checks the context first. How many calls reach the fake?",
            "A zero value with a nil error is a success. What does readOnce return?",
            "%w keeps the original in the chain. Does errors.Is find the cause?",
            "A digest changes when any byte changes. Does the source with an extra space match?",
        ),
        steps=(
            "The fake now returns 4, so `v==3` fails while the error is nil and Calls is 1. The adapter works; the fake's value changed.",
            "readOnce calls the fake exactly once, so `f.Calls!=1` is false and the check fails. Restore `==1`; the call count is part of the evidence.",
        ),
    ),
    "go-048": dict(
        predict="Predict the state and write count after reconciling u1 from 1 to 3, and after running the same request twice. Predict what happens when the expected UID is old but the observed one is new, when the desired count is negative and when the context is already canceled. Then predict the write count after a restart from converged state.",
        pitfall="A capstone controller usually fails at the edges, not on the happy path: writing even when observed state already matches, acting on a recreated object with the same name, mutating before validating intent, or starting new work after cancellation. Order the checks as context, ownership, validation, then a write only when state differs. Count writes in tests to prove idempotence.",
        retrieval="Design a reconcile function for a ConfigMap-like object with an owner UID, desired data and observed data. Write tests for convergence, repeated runs, ownership mismatch, invalid input, cancellation and restart from saved state, asserting the write count in each. Then draw its state diagram and mark which transitions perform external side effects.",
        transfer="This checklist carries into any reliable background system, not only Kubernetes: validate intent, confirm identity, honor cancellation, write only when state differs and prove each property with a test that counts effects. Apply it to a job runner, a sync service or a migration tool, and document the operational contract alongside the code.",
        hints=(
            "Current differs from desired. What do Current and Writes become?",
            "The second call finds Current already 3. Does it write again?",
            "The expected UID differs from the observed one. Does any field change?",
            "Validation runs before any write. What happens to Current?",
            "The context check runs first. Is any write recorded?",
            "The restored state already matches. Does Writes change?",
        ),
        steps=(
            "Reconciling to 4 sets Current to 4, so `s.Current==3` fails while Writes is 1. Convergence works; the desired count changed.",
            "The second call now wants 4, so it performs a second write and `s.Writes==1` fails. Restore 3 so the repeat matches the converged state.",
        ),
    ),
}

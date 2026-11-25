"""Lesson-specific teaching text for go-037 to go-042 (see teaching.py)."""

PART5 = {
    "go-037": dict(
        predict="Predict plan's action for each observation: no child, a child at 2, a child already at 3 and a negative request. Then predict the second plan after an update is applied, and the two plans for scaling an existing child to zero. Decide which result shows that running reconcile twice is safe.",
        pitfall="Edge-triggered thinking is the trap: a reconciler that acts on what an event says happened, such as replica added, instead of reading current state. Events can be dropped, merged or replayed, so the loop must compute from observation every time. Validate intent before acting, and treat an existing child as normal; a reconcile that always creates fails on its second run.",
        retrieval="Write `planConfig(want string, exists bool, current string) string` returning create, update, none, or invalid for an empty want. Test all four results, and a sequence that applies each plan and plans again until it reaches none. Then explain why scale-to-zero is an update rather than a delete in this model, and what would change if deletion were intended.",
        hints=(
            "No child exists yet. Which branch of plan runs after validation?",
            "The child exists but holds 2. Which comparison decides the action?",
            "Observed equals desired. What does a converged plan return?",
            "Validation runs before existence is checked. What does a negative count produce?",
            "After the update is applied, current equals desired. What is the second plan?",
            "Zero is valid desired state. Which actions take 2 to 0 and then settle?",
        ),
        steps=(
            'With exists set to true, plan compares 3 with 0 and returns update, so `=="create"` fails. The planner is right; the edited observation claims a child already exists.',
            'A child at 3 already matches desired, so plan returns none and `=="update"` fails. Restore the observed count of 2.',
        ),
    ),
    "go-038": dict(
        predict="Predict the value and version after an update that carries the current token, and after one that carries a stale token. For the reread case, predict the value written when the increment is computed from the fresh read. Then decide whether the update function ever compares tokens by order, and predict the conflict count after two stale attempts.",
        pitfall="Retrying a conflicted write with the same object is the common error: the stale token conflicts forever, or, if the token is dropped, the write clobbers a newer change. On conflict, reread, recompute from current state and retry within a bound. Do not parse resourceVersion as a number, and do not send whole objects when you own only some of their fields.",
        retrieval="Write `incrementWithRetry(get func() Versioned, update func(observed string, value int) error, attempts int) error` that rereads after each ErrConflict and gives up when the budget is spent. Test it with a store that conflicts once, one that always conflicts and one that never does. Then explain why recomputing after the reread matters more than the retry itself.",
        transfer="client-go's retry.RetryOnConflict wraps exactly this loop for Kubernetes updates: get the latest object, apply your change, update, and retry only on a conflict error. Server-side apply narrows the problem further by tracking field ownership. Use the same shape for any store with ETags or row versions, such as an HTTP API that honors If-Match.",
        hints=(
            "The supplied token equals the current one. What do Value and Version become?",
            "The token a is stale against b. Does the update change anything?",
            "The write uses the freshly read token and value. What is the result?",
            "versionUpdate compares tokens only for equality. Does their format matter?",
            "The update touches Value and Version only. What happens to Labels?",
            "Each attempt carries the same stale token. How many conflicts, and what value?",
        ),
        steps=(
            "The update now writes 4, so `s.Value==3` fails while the token still becomes b. The version check passed; the written value changed.",
            "Starting at Value 4, the conflict correctly leaves 4, so `s.Value==3` fails. Restore the initial 3; the stale write still changes nothing.",
        ),
    ),
    "go-039": dict(
        predict="Predict the cache after an ADDED event and after a MODIFIED event for the same key. For a bookmark, predict the version and the number of items. Predict what an expired-history signal sets and returns, the cache after deleting a key twice, and the result of an event kind the cache does not know.",
        pitfall="Treating a watch as a durable log is the main error: connections drop and history expires, so a client that only resumes from its last version eventually gets an expired error and must relist. Another mistake is ignoring bookmarks, which advance the version without objects. Deletes must be idempotent, and unknown event types should fail loudly rather than be guessed at.",
        retrieval="Write a cache that applies ADDED, MODIFIED, DELETED and BOOKMARK events and records the last version. Replay a short sequence, then inject an expired signal and implement relist as replacing all items from a snapshot with its version. Check that items deleted during the gap disappear, and explain why replaying events alone could not remove them.",
        transfer="Informers in the next lessons run this list-then-watch loop for you, including the relist on expiry. Knowing the model tells you what to expect: after a relist, handlers may see updates for objects that did not change, and some deletions arrive only as missing items. Write handlers that converge from current state rather than counting events.",
        hints=(
            "ADDED stores the key with its value. What does demo hold?",
            "MODIFIED replaces the stored value. What is demo after the second event?",
            "A bookmark carries a version but no object. What changes?",
            "EXPIRED sets a flag and returns an error. What do err and NeedsList hold?",
            "delete on a missing key is a no-op. How many items remain?",
            "The default branch rejects unknown kinds. What does applyWatch return?",
        ),
        steps=(
            'The event now carries value 3, so the cache holds demo=3 and `s.Items["demo"]==2` fails. Applying the event works; the payload changed.',
            'The modification now carries 4, so the cache holds 4 and `s.Items["demo"]==3` fails. Restore the value 3 in the event.',
        ),
    ),
    "go-040": dict(
        predict="Predict the delay for attempts 0, 1 and 2, and for attempts 3 and 10. Predict how many pending identities remain after enqueuing alpha, alpha and beta into a set. Predict which failure classes are retried, the delay after a key's history is cleared, and how many retries fit in a total budget of 10 units.",
        pitfall="Retrying every error is the classic queue bug: a validation failure retried forever burns API quota and fills logs with no chance of success. Classify errors, retry only transient ones and surface the rest. Uncapped exponential delay grows without bound, and forgetting to reset a key after success makes its next unrelated failure start at the maximum delay.",
        retrieval="Write `nextDelay(attempt, base, max int) int` with doubling and a cap, and `shouldRetry(err error) bool` that retries only errors wrapping a transient sentinel. Test delays for attempts 0 through 5 and classification for wrapped and unwrapped errors. Then explain why coalescing duplicate keys is safe for a level-based reconciler.",
        transfer="client-go's workqueue implements this policy: Add coalesces keys, AddRateLimited applies per-key backoff and Forget resets it after success. The same decisions apply to any background worker calling a remote service: classify errors, cap delays, add jitter in production and bound total effort with a deadline so one stuck key cannot consume the whole budget.",
        hints=(
            "delay shifts 1 left by the attempt. What are the first three values?",
            "Attempts at or beyond 3 return the cap. What are delay(3) and delay(10)?",
            "A set keeps one entry per key. How many keys remain?",
            "Only the transient class returns true. Which class is retried?",
            "A missing key reads as attempt 0. What delay does that give?",
            "The loop stops when the next delay would pass 10. Which delays fit?",
        ),
        steps=(
            "delay(1) is 2, so `delay(1)==1` is false and the growth check fails. The function is right; the edited check reads the wrong attempt.",
            "delay(3) returns the cap of 8, so `delay(3)!=8` is false and the cap check fails. Restore `==`.",
        ),
    ),
    "go-041": dict(
        predict="Predict which inputs validateTarget accepts: an HTTPS endpoint with a namespace and context, an HTTP endpoint, a missing context name and a namespace containing a slash. Predict the method and URL path of the built list request. Then decide why an endpoint carrying a username and password is rejected even over HTTPS.",
        pitfall="Letting a program use whatever current-context the local kubeconfig names is how lesson code ends up writing to a production cluster. Require an explicit context and namespace, and reject plain HTTP and credentials embedded in URLs. On the dependency side, mismatched k8s.io/api, apimachinery and client-go versions cause confusing compile errors; pin them together and check the compatibility matrix.",
        retrieval="Write `loadTarget(env map[string]string) (Target, error)` that reads endpoint, namespace and context from explicit keys and validates them with this lesson's rules, adding a namespace length limit. Test missing keys, HTTP, userinfo and a valid set. Then explain what a kubeconfig exec plugin can do and why that makes the file itself a credential.",
        transfer="Every later lesson that touches a cluster starts from configuration like this. In real tools, build the rest.Config from an explicitly named kubeconfig context, print the target before mutating anything and refuse to run when the context is unset. Apply the same discipline to cloud SDKs and database connection strings: authority should never come from an ambient default.",
        hints=(
            "Every rule passes for an HTTPS endpoint with names. What does validateTarget return?",
            "The scheme must be https. What happens to http?",
            "An empty context name fails the explicit-name rule. Is it accepted?",
            "The namespace may not contain a slash. Which rule rejects lesson/other?",
            "Building a request does not send it. What are its method and path?",
            "URL.String writes userinfo into the endpoint. Which rule catches it?",
        ),
        steps=(
            "The port is now 6443!, so url.Parse fails, validateTarget returns an error and `==nil` is false. The validator is right; the endpoint no longer parses.",
            "An HTTP endpoint is rejected, so validateTarget returns an error and `==nil` is false. Restore `!=nil` so the check asserts rejection.",
        ),
    ),
    "go-042": dict(
        predict="Predict the cached label after a copy made with copyCached is changed, and after a plain struct assignment is changed. For the stale view, predict the version the cache shows and the server's latest. Predict whether the processor runs before sync, and which version a queued key reads after the store updates.",
        pitfall="Mutating an object returned by an informer lister is the classic shared-cache bug: struct assignment copies the map header, not the map, so the change leaks into every reader and corrupts later comparisons. Call DeepCopy before editing. A cache read right after your own write may also be stale; do not treat absence or an old version as proof that the write failed.",
        retrieval="Write `deepCopyPod(p Pod) Pod` for a struct with a labels map and a slice of container names. Test that changing the copy's label and appending to its slice leave the original unchanged. Then write a processor that refuses work until a synced flag is true, and explain why a queue holds keys rather than objects.",
        transfer="In client-go, listers return pointers into the shared informer cache, and generated types provide DeepCopy for exactly this reason. Read from the lister, copy, change, then write through the client. Expect the cache to lag your own writes, and let the next reconcile, triggered by the watch event, observe the result instead of polling the cache.",
        hints=(
            "copyCached builds a new map. Which value does the cache keep?",
            "Assignment copies the map reference. Which map does shallow change?",
            "Only one event was delivered. Which version does the cache show?",
            "process refuses work before sync. What do the two calls return?",
            "The key is resolved when processed. Which version is in the store then?",
            "The copy owns its own map. How many labels does each hold?",
        ),
        steps=(
            'The cached label key is now app!, so `cached.Labels["app"]` is empty and the check fails. copyCached still isolates the copy; the fixture lost its app key.',
            'The write now goes to app!, so `cached.Labels["app"]` stays web and the counterexample check fails. Restore the app key; the shared map still shows the defect.',
        ),
    ),
}

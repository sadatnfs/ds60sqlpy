"""Lesson-specific teaching text for go-023 to go-028 (see teaching.py)."""

PART3 = {
    "go-023": dict(
        predict="Predict which of these is a transport error and which is an HTTP failure: a canceled context, a 404 response and a 500 response. For the body limit, decide why fetch reads limit plus one bytes and predict the result for exactly four bytes under a limit of four. Then predict what happens to the response body if the status check returns early.",
        pitfall="The classic client bugs are treating any response without a transport error as success, so a 404 or 503 body is parsed as data, and forgetting to close the body, which leaks connections. Reading a body with io.ReadAll and no limit lets a misbehaving server exhaust memory. Note that fetch accepts only 200 here; a real client should state which statuses its caller treats as success.",
        retrieval="Write `getJSONLength(ctx, client, url string, limit int64) (int, error)` that rejects non-2xx statuses with the status code in the error, closes the body on every path and rejects bodies over the limit. Test it with a fake RoundTripper for success, 404, an oversized body and a canceled context. Then explain who owns the response body and when ownership ends.",
        transfer="Every remote call in later lessons has three failure layers: the transport, the protocol status and the payload. The Kubernetes client wraps HTTP the same way, so an API conflict or a not-found object is a status, not a broken connection. Keep a context deadline on every call, bound what you read and make the caller decide which statuses count as success.",
        hints=(
            "The fake transport returns the status you pass in. Which status does fetch accept?",
            "A 404 is a valid HTTP response. Which line of fetch turns it into an error?",
            "fetch reads limit plus one bytes. What does a fifth byte prove when the limit is four?",
            "The fake transport checks the request context first. Which error does a canceled context produce?",
            "Exactly four bytes under a limit of four is not excess. Does `len(data)>limit` hold?",
            "An empty body is a valid payload. What should the string and error be?",
        ),
        steps=(
            "fetch accepts only status 200, so 201 returns a status error and `err==nil` fails. The transport succeeded; the helper's success rule rejected the status.",
            "The 404 path returns an error, so `err==nil` is false and the check panics. An HTTP failure status must surface as an error; restore `err!=nil`.",
        ),
    ),
    "go-024": dict(
        predict="Predict what the program would print if main returned before receiving from result, and whether the goroutine is guaranteed to finish first. For the three tasks, predict what wg.Wait guarantees about the buffered channel. For the start boundary, predict whether the premature select can ever take the receive case before close(start) runs.",
        pitfall="Starting a goroutine without a join is the defining mistake: main may return first, or a test may check a value before it is written. Sleeping to wait for completion only hides the race. A second bug is calling wg.Add inside the goroutine, where Wait can run before Add. Finally, never read a shared variable a goroutine writes unless a channel, WaitGroup or lock orders the two.",
        retrieval="Start five goroutines that each send their index times ten on a buffered channel, join them with a WaitGroup and sum the received values; check that the sum is 100. Then explain where wg.Add must be called and why. Finally, describe what could go wrong if you replaced the WaitGroup with a short sleep.",
        transfer="Every concurrent design in later lessons needs an explicit answer to the question: who waits for this goroutine, and how does its result become visible? Channels, WaitGroups, errgroup and contexts are all answers to it. When a controller starts informers or a server starts handlers, trace the join and the shutdown path before trusting the happy path.",
        hints=(
            "Receiving from an unbuffered channel waits for the sender. What value does the goroutine send?",
            "wg.Wait returns after every Done. How many signals does the buffered channel hold then?",
            "Each goroutine receives its own x. Which two squares are sent?",
            "The worker blocks on start. Which statement releases it, and what does it send next?",
            "A select with default never blocks. Can the receive case win while the worker still waits?",
            "The receiver adds every value. Which four squares make up the sum?",
        ),
        steps=(
            "The goroutine now sends 7*7, so the receive yields 49 and `<-result==42` fails. The join works; the computation changed.",
            "Starting the loop at 1 launches only two tasks, so wg.Wait returns with two markers and `len(done)==3` fails. Restore the initial 0 so three tasks start.",
        ),
    ),
    "go-025": dict(
        predict="Predict whether range over the buffered channel ends before or after both values are received, and what happens if close is removed. For the zero-and-closed case, predict both value and ok for each receive. For the nil select arm, decide whether it can ever be chosen, and for the slice case, predict the received element after the original is changed.",
        pitfall="Closing a channel from the receiver, or from one of several senders, is the classic ownership bug: a later send panics. Only the sender that knows no more values will come should close. A related surprise is treating a receive of zero as a real message; use comma-ok when closure matters. Buffering also does not copy referenced data, so a slice sent through a channel is still shared.",
        retrieval="Write a producer that sends the words of a sentence on a channel it owns and closes, and a consumer that counts them with range. Check the count, then add a second receive after the loop and check with comma-ok that the channel reports closed. Explain which goroutine is allowed to close, and why.",
        hints=(
            "range over a channel stops after close and drain. Which values remain in the buffer?",
            "A closed channel yields zero values forever. Which return value separates a real 0 from closure?",
            "produce defers close after its sends. How many values does range receive?",
            "len reports buffered values and cap the capacity. What do both hold with no receiver?",
            "A receive from a nil channel blocks forever. Which arm can proceed?",
            "append onto a nil slice copies the elements. Which storage does the receiver see?",
        ),
        steps=(
            "The buffer now holds 3 and 3, so the drained sum is 6 and `sum==5` fails. Draining still works; the first value changed.",
            "The first receive yields 1, not 0, so `a==0` fails although okA and !okB still hold. The closure semantics are fine; restore the sent zero.",
        ),
    ),
    "go-026": dict(
        predict="Predict Err for a context before and after its cancel function runs. For the tree, predict which contexts become canceled when the parent is canceled, and which when only the child is. For the deadline at Unix time zero, predict Err immediately after construction, and for contextValue, predict both return values with a canceled and a live context.",
        pitfall="Contexts are cooperative, so the common mistake is assuming cancellation interrupts work: a function that never checks ctx.Err or ctx.Done keeps running. Another is discarding the cancel function, which leaks timers and children until the parent ends; go vet reports this. Do not store a context in a struct for later calls, and do not use context values for ordinary optional parameters.",
        retrieval="Write `sumUntil(ctx context.Context, items []int) (int, error)` that checks ctx.Err before each element and returns the partial sum with the context error. Test it with a live context, an already canceled context and a parent that is canceled after its child is derived. Then explain why canceling the child leaves the parent untouched.",
        hints=(
            "Calling cancel marks the context done. Which sentinel does Err report afterward?",
            "Cancellation flows from parent to child. What do both Err calls return?",
            "Canceling a child never reaches upward. What does the parent's Err return?",
            "A deadline in the past is already expired. Which sentinel does Err report?",
            "contextValue checks Err before computing. What does it return for a canceled context?",
            "With a live context the check passes. What is twice 4?",
        ),
        steps=(
            "After cancel, Err is exactly context.Canceled, so `!=` is false and the check panics. The context behaves correctly; the edited comparison asserts the opposite.",
            "Canceling the parent sets its Err to context.Canceled, so `parent.Err()!=context.Canceled` is false and the tree check fails. Restore `==` for the parent too.",
        ),
    ),
    "go-027": dict(
        predict="Predict the final count with four workers doing 100 locked increments, and what could happen if Inc skipped the lock. For the pair, decide why A and B need one mutex rather than two atomics. Predict how many times the Once body runs, and the result of each compare-and-swap when the second reuses the old expected value.",
        pitfall="Locking writes but reading without the lock is still a data race, and the race detector, not a passing run, is the evidence. A second mistake is protecting each field of a compound invariant separately, so another goroutine can observe A decreased before B increased. Atomics suit single values; use a mutex when several fields must change together, and copy no struct that contains a mutex.",
        retrieval="Write an Inventory type with a mutex protecting reserved and available counts, and a Reserve(n) method that moves n units only when enough are available. Run eight goroutines reserving one unit each from five available units and check that exactly five succeed and the total is unchanged. Then explain why two atomic counters could not enforce this.",
        hints=(
            "Each Inc locks before incrementing. How many increments do four workers make?",
            "atomic.Int64 adds without a lock. What does Load return after both additions?",
            "Transfer changes both fields under one lock. What do A, B and their sum become?",
            "sync.Once runs its function at most once. How many times does n increase?",
            "CompareAndSwap succeeds only when the current value equals the expected one. What is it after the first swap?",
            "Snapshot reads both fields under the lock. Can an unchanged pair ever show another total?",
        ),
        steps=(
            "Starting the loop at 1 starts three workers, so the count is 300 and `c.Value()==400` fails. Locking works; the number of workers changed.",
            "The first Add now adds 4, so Load returns 8 and `n.Load()==7` fails. The atomic operations are correct; restore the 3.",
        ),
    ),
    "go-028": dict(
        predict="Predict the order in which results arrive from two workers squaring 3, 1 and 2, and the order of the returned slice. For empty input, decide which goroutine closes results and why the collector still terminates. Predict the error for zero workers, and whether four workers with one input leave any goroutine blocked.",
        pitfall="Appending results in completion order is the usual bug: it passes with one worker and fails intermittently with several. Give each task an index and place results by it. The other common failure is a deadlock from closing results too early, or never, because the closer does not wait for every worker. An unbounded number of workers is not a pool; validate the bound before starting goroutines.",
        retrieval="Write `parallelLengths(words []string, workers int) ([]int, error)` that returns word lengths in input order using an index on each task. Test it with one worker and with three on the same input, with empty input and with zero workers. Then explain which goroutine closes the results channel and what it waits for first.",
        hints=(
            "Results are placed by Index, not arrival. Which square belongs at position 0?",
            "With no jobs, every worker exits at once. What closes results so the collector ends?",
            "The bound is validated before any goroutine starts. What does zero workers return?",
            "Placement by index removes timing from the output. Do one and three workers differ?",
            "Each task carries its own index. Are three equal inputs merged into one result?",
            "Idle workers exit when jobs closes. How many results does one input produce?",
        ),
        steps=(
            "The first input is now 4, so `v[0]` is 16 and `v[0]==9` fails while 1 and 4 stay in place. Ordering is correct; the first input changed.",
            "Empty input is a success, so err is nil and `err!=nil` is false. The pool returns an empty slice without error; restore `err==nil`.",
        ),
    ),
}

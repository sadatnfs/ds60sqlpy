## An experiment must make a claim falsifiable

A runtime check needs a stated input, an expected observation and a boundary on
what it establishes. A process exiting with zero tells you that its own success
path completed. It does not prove a query's semantics, durable state, distributed
recovery or acceptable latency. Those are separate claims with different oracles.
The most useful checks expose the assumptions that a plausible implementation
could violate while still appearing to work.

An oracle is an independent way to decide whether an observation is correct.
For a three-order fixture, list the expected order identities and derive the sum
by hand. Do not compute the expected answer using the same join that is under
test. Otherwise a duplicate dimension can inflate both answers identically and
leave the check green. For recovery, capture an identity before interruption and
compare it after the exact operation whose behavior you want to establish.

This chapter executes actual local DataFusion queries and compares deliberately
incorrect alternatives. It also represents operational evidence as a small
explicit record. That record is a claim ledger, not fabricated service telemetry.
The real Arrow Flight and Kafka workshops supply the corresponding actual
positive, negative and lifecycle experiments once those projects are prepared.

## Worked case A: reject a superficially plausible answer

The valid query joins three orders to one row per known customer. Its result must
retain three order identities and total 20. A duplicate dimension then creates
four joined rows and total 24. Both are legal SQL results; the independent
business oracle rejects the second as an invalid enrichment. The example catches
the assertion intentionally and prints the difference, so a learner can see why
SQL validity is weaker than metric validity.

The fixture includes an unknown customer to expose accidental population loss.
Checking only the total can miss structural problems when duplicated positive
amounts and dropped records happen to cancel. The oracle therefore checks row
identity multiplicity and the amount total. In a production pipeline, this pattern
becomes key coverage, uniqueness, reconciliation and domain-specific quality
rules rather than a single universal equality assertion.

The query is ordered before rows are compared. Relational output order is not
guaranteed without an ordering clause, and changing parallelism can reveal that
assumption. A correct unordered multiset comparison is another option. Choosing
between sequence and multiset equality is part of defining the result contract,
not merely a test implementation detail.

## Worked case B: separate restart survival from availability

The evidence ledger distinguishes same-container resume, replacement with retained
volume, and availability during failure. A same-container restart can establish
that one process recovered and found its local data. Replacing the container while
retaining the named volume tests a different storage boundary. Neither proves the
service remained reachable while its only process was stopped.

The code refuses to derive an availability claim from a ledger containing only
restart evidence. It then shows the additional categories that a real availability
experiment would require: requests during the outage, bounded timing, a defined
success criterion and multiple replicas or an alternative serving path. These
are not run by this ordinary pad. The ledger deliberately records them as absent
rather than substituting an in-memory toy cluster for the product.

For a failure test, capture the exact resource, initial state, interruption,
observed errors and final state. A timeout is not proof that the intended policy
rejected an input. A missing executable, DNS failure and invalid replication
factor can all produce nonzero status for unrelated reasons. Inspect the actual
diagnostic and verify that the expected state was preserved after rejection.

## Diagnosis and interview discussion

Use deterministic correctness checks for the small fixture and repeated timed
measurements for performance. Keep the workload, warmup, concurrency, hardware
and source version explicit. The simple identity \(\mathrm{throughput}=N/T\)
needs a stated interval and definition of completed work. A tiny local result
cannot justify linear extrapolation to a large cluster with different I/O and
coordination behavior.

**Interview discussion: what does a successful restart test prove?** It proves
only the state transition and readback you actually observed on that topology.
Specify whether the container was reused or replaced, whether storage persisted,
whether requests failed during interruption and whether data was lost or
replayed. The two cases teach how an independent oracle and an honest evidence
ledger prevent a working demonstration from becoming an unsupported reliability
claim.

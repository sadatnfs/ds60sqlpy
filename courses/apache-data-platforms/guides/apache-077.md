# apache-077: Snapshots, predicates and consistency

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-076`, `apache-075`.

## Reproducibility requires selecting a table state

A mutable table name identifies a logical object whose current contents can
change. A version-pinned request identifies a selected table state under the
server's supported protocol and retention rules. Saving only the name and query
text is insufficient when a later read can observe additional commits. Record
table identity, selected version, schema and result identity together.

Predicate hints can help a server reduce eligible files or other work. They are
not automatically an authorization policy or a complete row-level filter.
The recipient must preserve SQL/predicate correctness according to its supported
reader semantics. An optimization hint that the server ignores should not make
a correct client return unfiltered business results.

The prepared fixture client requests version 0 and no predicate hints, making its
first oracle explicit and small. More advanced predicate and historical features
need separate actual server/client acceptance. Configuration showing
historyShared does not prove every version remains readable after retention or
that every client supports the same request fields.

## Worked case A: compare a pinned and current read

Prepare the three-order version 0 table and record its exact result. Append a
fourth west order with amount2using the actual compatible table writer, creating
a new committed version. Query the old version through a supported historical
request and separately query current state. The old oracle remains three orders
and total 20; the new oracle contains the fourth ID and total 22.

Both results can be correct because they answer against different states. A
recipient cache that keeps version 0does not automatically follow the provider's
newest commit. Conversely, a client that refreshes current state during a retry
can change the data underlying a supposedly reproducible report. Make that
refresh policy visible rather than hiding it behind the same table name.

The protocol response should confirm the selected version when required by the
chosen operation. A client cannot simply assume the server honored a request
field because the HTTP status was successful. Check the returned state identity
and fail explicitly if the requested historical boundary is unsupported or absent.

## Worked case B: compare a hint with client-side truth

Request only east orders through a supported predicate-hint path on the real
server, then apply the intended row predicate in a compatible recipient reader.
The independent expected IDs are1and3 with total 11. Compare this with a no-hint
request over the same version. Correctness must match even if the hint changes
which files are returned or how much data is transferred.

Partition/file statistics can eliminate whole files while leaving nonmatching
rows within retained files. Therefore file pruning does not necessarily equal
row filtering. Record both eligible-file observations and final row identities
rather than treating a smaller file list as proof of the requested business
predicate.

A user-supplied hint must never be treated as the sole access-control boundary.
If a provider intends to expose only a subset, it needs actual supported policy
or a separately published data product with an enforceable scope. A curious
recipient may issue a different allowed request, so optimization syntax cannot
safely stand in for authorization.

## Diagnosis and interview discussion

Inspect requested/returned version, history policy, retention, schema, predicate
representation and recipient filtering behavior. Distinguish unsupported history
from missing files and distinguish ignored hints from incorrect client filtering.
Keep retries bound to the intended table state when reproducibility matters.

**Interview discussion: does a predicate hint guarantee row-level security?** No.
It is part of query optimization unless the actual protocol/deployment explicitly
provides a tested policy guarantee. These cases separate fixed-state reproducibility
from file pruning and final row correctness.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Delta Sharing apache-077 prepared command notebook

Copy the owned Delta Sharing project and follow PREPARATION.md. Delta Sharing
belongs to Delta Lake/Linux Foundation. The offline preparation actions are:

```bash
bash run.sh prepare
bash run.sh plan
```

For a separately prepared actual owned reference server and untracked recipient
profile, the bounded native Docker protocol client runs with:

```bash
bash run.sh check
```

The fixture contract pins version 0. Append/current-versus-history and predicate-hint experiments require a compatible actual writer/server/client and separate oracles; no hint is treated as an access policy.

The classroom Markdown pad does not start a service. Source configuration and
unit policy fixtures are not actual reference-server receipts. Keep credentials
and signed URL query strings out of all published source and evidence.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)

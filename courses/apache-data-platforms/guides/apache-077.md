# apache-077: Snapshots, predicates and consistency

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-076`, `apache-075`.

## Key terms

- **Table version:** A specific committed state of a shared Delta table. Requesting it pins the result so later commits do not change the answer.
- **Predicate hint:** A filter the client sends so the server may skip files. The server can ignore it, so the client must still apply the full filter.
- **History sharing:** A provider option that makes earlier table versions readable, still subject to the table's retention rules.
- **Result identity:** The recorded table, version, schema and row values that let a later read be compared with the original one.

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

**Execution boundary.** Both comparisons need a prepared reference server and a table
writer, which the repository does not provide. The row oracles below are written
answers derived from the fixture, not observed responses.

## Worked case A: compare a pinned and current read

Prepare the three-order version 0 table and record its exact result. Append a
fourth west order with amount 2 using the actual compatible table writer, creating
a new committed version. Query the old version through a supported historical
request and separately query current state. The old oracle remains three orders
and total 20; the new oracle contains the fourth ID and total 22.

Both results can be correct because they answer against different states. A
recipient cache that keeps version 0 does not automatically follow the provider's
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
The independent expected IDs are 1 and 3 with total 11. Compare this with a no-hint
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

## Worked examples

### Query the table at a pinned version

```bash
curl -s -H "Authorization: Bearer $RECIPIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version": 0, "predicateHints": []}' \
  "$SHARING_ENDPOINT/shares/ds60_fixture/schemas/tutorial/tables/orders/query"
```

The response is newline-delimited JSON: a protocol line, a metaData line and one file line per data file, each with a short-lived presigned URL. The delta-table-version response header must equal 0, or the reader cannot claim it saw the pinned state. Two reads at version 0 return the same files; a read without a version follows the latest commit and can change between calls, which is why reproducible reports always pin.

### Predicate hints do not filter rows

```json
{
  "version": 0,
  "predicateHints": ["region = 'east'"]
}
```

A server may use hints to skip files whose statistics cannot match, but it is allowed to ignore them, and the reference configuration sets evaluatePredicateHints to false. The client must therefore apply the filter itself after reading. If a recipient relied on hints to hide west rows, it would receive them anyway, so hints are an optimization and never an access boundary.

## Complete worked source

The classroom does not execute these service commands. See the [workshop rules](../STUDY-GUIDE.md#workshop-notebooks).

# Delta Sharing apache-077 prepared command notebook

`fixture-contract.json` in the copied Delta Sharing project pins version 0. These two actions confirm the client image and print the rows that version should hold:

```bash
bash run.sh prepare
bash run.sh plan
```

Against an owned server prepared at version 0, `check` sends that version with an empty `predicateHints` list and confirms the `delta-table-version` header before accepting rows:

```bash
bash run.sh check
```

The fixture contract pins version 0. Append/current-versus-history and predicate-hint experiments require a compatible actual writer/server/client and separate oracles; no hint is treated as an access policy.

Predicate hints let a server skip files; they never filter rows for security. A history test needs a writer that commits version 1 and a separate oracle for each version you read.

## Primary references

- [Delta Sharing protocol](https://github.com/delta-io/delta-sharing/blob/v1.4.1/PROTOCOL.md)
- [Reference server and client examples](https://github.com/delta-io/delta-sharing/blob/v1.4.1/README.md)
- [Reference server configuration](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/universal/conf/delta-sharing-server.yaml.template)
- [Actual cloud signing implementation](https://github.com/delta-io/delta-sharing/blob/v1.4.1/server/src/main/scala/io/delta/sharing/server/common/CloudFileSigner.scala)
- [Current Python package dependencies](https://pypi.org/project/delta-sharing/1.4.2/)

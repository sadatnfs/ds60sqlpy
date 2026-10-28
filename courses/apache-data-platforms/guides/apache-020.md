# apache-020: Embedding an analytical engine

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-017`, `apache-018`, `apache-019`.

## Embedding an engine is an application-design decision

An embedded engine gives a program analytical operators without a separate query
server. The application still decides which data is visible, which operations a
caller may request, how much output can be collected and how failures are reported.
An engine that can read arbitrary paths or execute arbitrary SQL is a much broader
capability than a fixed reporting endpoint. A small wrapper should expose only
the behavior its product actually needs.

This chapter builds a local query function, not an HTTP service. Each request
creates an isolated DataFusion session over a fixed synthetic Arrow table. The
public request consists of a region selected from an allowlist and an integer row
limit within a small bound. It does not accept a table name, filesystem path,
SQL expression, URL or compiler command. Actual service networking and process
lifecycle are studied in the separate Flight and data-product projects.

A SQL LIMIT bounds returned rows, but does not generally bound all input scanned,
join state, sort work or execution time. The fixture is separately bounded to
three rows, and the real classroom container supplies independent CPU, memory,
process and timeout limits. A useful service design combines input, computation
and output limits instead of assuming one clause solves every resource concern.

## Worked case A: a narrow reporting request

The accepted request selects east-region rows and asks for at most two records.
The implementation validates parameters before creating a session, registers only
the fixed orders table and chooses a constant query template for that region.
The returned rows are ordered by order ID so the caller can reproduce the result.
The exact oracle expects orders 1 and 3, totaling 11.

The region value never becomes a fragment of arbitrary SQL. A dictionary maps
approved region identifiers to prewritten complete query strings, and the limit
is checked as an integer before it is inserted. In this tiny teaching design,
that combination creates a narrow interface without relying on escaping arbitrary
text. A richer application should use the engine's supported parameter mechanism
and still validate resource and authorization boundaries.

The output includes a SHA256 of the canonical source rows, the accepted request
and the result rows. This makes the response interpretable after the process exits.
A digest supplies byte identity, not authorization, provenance from an external
organization or a guarantee that the source is scientifically valid. The fixture
is synthetic and that limitation stays visible.

## Worked case B: reject unapproved behavior before execution

The negative cases submit a SQL-like region string, an oversized limit, a Boolean
limit and an unexpected request field. Each fails validation before the engine is
created. Python treats bool as a subclass of int, so a naive isinstance check can
accidentally admit true as a one-row limit. The explicit type check makes the
intended request schema unambiguous.

Two successful requests use separate sessions. A caller cannot register a table
in one request and have it leak into another session through this wrapper. This
is session isolation inside one trusted local program, not a sandbox for hostile
multi-tenant users. The implementation does not claim protection against arbitrary
Python execution, a compromised process or a container administrator.

The program also checks the serialized response size. A row limit alone is not
enough when strings or nested values can be large. This fixture's short strings
make the bound easy to verify. Production output validation needs explicit column,
cell and encoding limits, and should keep an execution error distinct from a
failure to save a completed response.

## Diagnosis and interview discussion

Name the trust boundary before adding a query endpoint. Distinguish a trusted
analyst's local SQL pad from an application API serving fixed business questions.
Do not mount a host engine socket or unrelated credentials into an analytical
worker. Prepare dependencies before execution and keep learner state outside
images so replacing a process does not erase source or receipts.

**Interview discussion: is parameterized SQL enough to secure an analytics API?**
It prevents one class of query construction error when used correctly, but does
not define data authorization, allowed operations, computation cost, output size
or state isolation. The two cases implement a deliberately narrow interface and
show exactly what it admits and rejects, without presenting it as an unrestricted
production query service.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
import hashlib
import json

import pyarrow as pa
from datafusion import SessionContext

SOURCE = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 9},
    {"id": 3, "region": "east", "amount": 7},
]
QUERIES = {
    "east": "SELECT id,amount FROM orders WHERE region='east' ORDER BY id",
    "west": "SELECT id,amount FROM orders WHERE region='west' ORDER BY id",
}
created_sessions = 0


def query(request):
    global created_sessions
    if type(request) is not dict or set(request) != {"region", "limit"}:
        raise ValueError("Expected exactly region and limit")
    if type(request["region"]) is not str or request["region"] not in QUERIES:
        raise ValueError("Unapproved region")
    if type(request["limit"]) is not int or not 1 <= request["limit"] <= 3:
        raise ValueError("Limit must be an integer from one to three")
    created_sessions += 1
    ctx = SessionContext()
    ctx.register_record_batches("orders", [pa.Table.from_pylist(SOURCE).to_batches()])
    rows = (
        ctx.sql(QUERIES[request["region"]] + f" LIMIT {request['limit']}")
        .to_arrow_table()
        .to_pylist()
    )
    response = {
        "request": request,
        "source_sha256": hashlib.sha256(
            json.dumps(SOURCE, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "rows": rows,
    }
    assert len(json.dumps(response).encode()) <= 2048
    return response


first = query({"region": "east", "limit": 2})
assert first["rows"] == [{"id": 1, "amount": 4}, {"id": 3, "amount": 7}]
assert query({"region": "west", "limit": 1})["rows"] == [{"id": 2, "amount": 9}]
for request in [
    {"region": "east'; DROP TABLE orders;--", "limit": 1},
    {"region": "east", "limit": 99},
    {"region": "east", "limit": True},
    {"region": "east", "limit": 1, "path": "/tmp/private"},
]:
    before = created_sessions
    try:
        query(request)
    except ValueError as error:
        assert created_sessions == before
        print("Rejected before engine creation:", error)
    else:
        raise AssertionError("Invalid request accepted")
print(json.dumps(first, indent=2))
```

## Primary references

- [DataFusion embedding overview](https://datafusion.apache.org/library-user-guide/index.html)
- [DataFusion Python configuration](https://datafusion.apache.org/python/user-guide/configuration.html)

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

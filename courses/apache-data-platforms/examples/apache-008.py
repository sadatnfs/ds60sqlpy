from collections import Counter

import pyarrow as pa
from datafusion import SessionContext

ctx = SessionContext()
orders = pa.table({"id": [1, 2, 3], "customer": [1, 2, 99], "amount": [4, 9, 7]})
dimension = pa.table({"customer": [1, 2], "name": ["A", "B"]})
bad = pa.table({"customer": [1, 1, 2], "name": ["A", "A", "B"]})
for name, table in [("orders", orders), ("dimension", dimension), ("bad", bad)]:
    ctx.register_record_batches(name, [table.to_batches()])


def oracle(rows):
    assert Counter(row["id"] for row in rows) == Counter({1: 1, 2: 1, 3: 1})
    assert sum(row["amount"] for row in rows) == 20


for name in ["dimension", "bad"]:
    rows = (
        ctx.sql(
            f"SELECT o.id,o.amount FROM orders o LEFT JOIN {name} d "
            "ON o.customer=d.customer ORDER BY o.id"
        )
        .to_arrow_table()
        .to_pylist()
    )
    try:
        oracle(rows)
    except AssertionError:
        assert name == "bad"
        print("Independent oracle rejects duplicated enrichment:", rows)
    else:
        assert name == "dimension"
evidence = {
    "exact_container_resume": True,
    "retained_volume_replacement": True,
    "requests_during_outage": None,
    "replica_failover": None,
}
availability_demonstrated = all(
    evidence.get(key) is True for key in ["requests_during_outage", "replica_failover"]
)
assert not availability_demonstrated
print("Illustrative claim ledger, not measured service output:", evidence)
print("Availability during interruption:", availability_demonstrated)

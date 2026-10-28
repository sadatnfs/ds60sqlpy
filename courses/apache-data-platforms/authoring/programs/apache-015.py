import pyarrow as pa
from datafusion import SessionConfig, SessionContext, col, functions

records = [
    {"region": "east", "amount": 4},
    {"region": "west", "amount": 9},
    {"region": "east", "amount": 7},
    {"region": "west", "amount": -2},
]
table = pa.Table.from_pylist(records)
context = SessionContext(SessionConfig().with_target_partitions(2))
context.register_record_batches("events", [table.to_batches()])
sql = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM events "
        "WHERE amount > 0 GROUP BY region ORDER BY region"
    )
    .to_arrow_table()
    .to_pylist()
)
expressions = (
    context.table("events")
    .filter(col("amount") > 0)
    .aggregate([col("region")], [functions.sum(col("amount")).alias("total")])
    .sort(col("region").sort())
    .to_arrow_table()
    .to_pylist()
)
expected = [
    {
        "region": region,
        "total": sum(
            row["amount"] for row in records if row["region"] == region and row["amount"] > 0
        ),
    }
    for region in ["east", "west"]
]
assert (
    sql
    == expressions
    == expected
    == [{"region": "east", "total": 11}, {"region": "west", "total": 9}]
)
other = SessionContext(SessionConfig().with_target_partitions(2))
try:
    other.sql("SELECT * FROM events").collect()
except Exception as error:
    assert "events" in str(error) and (
        "not found" in str(error).lower() or "no table" in str(error).lower()
    )
    print("Independent session correctly lacks the events registration")
else:
    raise AssertionError("Expected a missing session registration")
other.register_record_batches("events", [table.to_batches()])
assert other.sql("SELECT COUNT(*) AS n FROM events").to_arrow_table()["n"].to_pylist() == [4]
print("SQL:", sql)
print("Expressions:", expressions)

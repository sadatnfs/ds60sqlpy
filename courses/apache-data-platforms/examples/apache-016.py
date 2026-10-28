import pyarrow as pa
from datafusion import SessionConfig, SessionContext

context = SessionContext(SessionConfig().with_target_partitions(2))
context.register_record_batches(
    "events", [pa.table({"region": ["east", "east", "west"], "amount": [4, 7, 1000]}).to_batches()]
)
query = "SELECT SUM(amount) AS total FROM events WHERE region = 'east' AND amount > 0"
assert context.sql(query).to_arrow_table()["total"].to_pylist() == [11]
plans = context.sql("EXPLAIN " + query).to_arrow_table().to_pylist()
assert plans and all(isinstance(row["plan"], str) and row["plan"] for row in plans)
for row in plans:
    print(row["plan_type"], row["plan"])
groups = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM events GROUP BY region HAVING SUM(amount) > 100"
    )
    .to_arrow_table()
    .to_pylist()
)
assert groups == [{"region": "west", "total": 1000}]
context.register_record_batches(
    "small_values", [pa.table({"region": ["east", "east"], "amount": [60, 60]}).to_batches()]
)
correct = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM small_values "
        "GROUP BY region HAVING SUM(amount) > 100"
    )
    .to_arrow_table()
    .to_pylist()
)
incorrect = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM small_values WHERE amount > 100 GROUP BY region"
    )
    .to_arrow_table()
    .to_pylist()
)
assert correct == [{"region": "east", "total": 120}] and incorrect == []
print("Group filtering:", correct, "incorrect row-level rewrite:", incorrect)

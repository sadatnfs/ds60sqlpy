import pyarrow as pa
from datafusion import SessionConfig, SessionContext

context = SessionContext(SessionConfig().with_target_partitions(2))
orders = pa.table({"order_id": [1, 2, 3], "customer_id": [1, 2, 99], "amount": [4, 9, 7]})
unique = pa.table({"customer_id": [1, 2], "segment": ["small", "large"]})
duplicate = pa.table({"customer_id": [1, 1, 2], "segment": ["small", "small", "large"]})
for name, table in [("orders", orders), ("customers", unique), ("duplicate_customers", duplicate)]:
    context.register_record_batches(name, [table.to_batches()])
assert len(set(unique["customer_id"].to_pylist())) == unique.num_rows
query = (
    "SELECT o.order_id, o.amount, c.segment FROM orders o LEFT JOIN customers c "
    "ON o.customer_id = c.customer_id ORDER BY order_id"
)
correct = context.sql(query).to_arrow_table().to_pylist()
assert correct == [
    {"order_id": 1, "amount": 4, "segment": "small"},
    {"order_id": 2, "amount": 9, "segment": "large"},
    {"order_id": 3, "amount": 7, "segment": None},
]
multiplied = (
    context.sql(query.replace("JOIN customers", "JOIN duplicate_customers"))
    .to_arrow_table()
    .to_pylist()
)
assert len(multiplied) == 4 and sum(row["amount"] for row in multiplied) == 24
assert sum(row["amount"] for row in correct) == 20
context.register_record_batches(
    "null_left", [pa.table({"key": pa.array([None], type=pa.int64())}).to_batches()]
)
context.register_record_batches(
    "null_right", [pa.table({"key": pa.array([None], type=pa.int64())}).to_batches()]
)
ordinary = (
    context.sql("SELECT COUNT(*) AS n FROM null_left l JOIN null_right r ON l.key = r.key")
    .to_arrow_table()["n"][0]
    .as_py()
)
null_safe = (
    context.sql(
        "SELECT COUNT(*) AS n FROM null_left l JOIN null_right r "
        "ON l.key IS NOT DISTINCT FROM r.key"
    )
    .to_arrow_table()["n"][0]
    .as_py()
)
assert ordinary == 0 and null_safe == 1
print("Unique dimension total:", 20, "duplicate dimension total:", 24)
print("Null ordinary matches:", ordinary, "null-safe matches:", null_safe)

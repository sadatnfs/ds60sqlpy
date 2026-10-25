"""cuda-039: CPU reference only, not CUDA execution."""

x = [1, 2, 3]
a = [2 * value for value in x]
# CPU sequential phases stand in for an explicit dependency edge.
b = [value + 1 for value in a]
assert b == [3, 5, 7]
edges = [("produce_A", "record_event"), ("record_event", "wait_B"), ("wait_B", "consume_B")]
print({"reference": b, "required_order_edges": edges})

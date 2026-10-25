"""Independent CPU reference with deterministic contract assertions."""

candidates = [
    {"name": "A", "memory": 8, "latency": 18, "quality": 0.95},
    {"name": "B", "memory": 12, "latency": 10, "quality": 0.96},
    {"name": "C", "memory": 6, "latency": 12, "quality": 0.80},
]
valid = [
    c["name"] for c in candidates if c["memory"] <= 8 and c["latency"] <= 20 and c["quality"] >= 0.9
]
assert valid == ["A"]
print("CPU decision fixture:", valid)

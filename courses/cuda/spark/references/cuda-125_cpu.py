"""Independent CPU reference with deterministic contract assertions."""

nodes = [{"name": "cpu-node", "gpu": 0}, {"name": "gpu-node", "gpu": 1}]
eligible = [node["name"] for node in nodes if node["gpu"] >= 1]
assert eligible == ["gpu-node"]
print("CPU scheduling worksheet:", eligible)

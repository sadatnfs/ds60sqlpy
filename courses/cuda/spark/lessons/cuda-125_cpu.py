"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

nodes = [{"name": "cpu-node", "gpu": 0}, {"name": "gpu-node", "gpu": 1}]
eligible = [node["name"] for node in nodes if node["gpu"] >= 1]
assert eligible == ["gpu-node"]
print("CPU scheduling worksheet:", eligible)

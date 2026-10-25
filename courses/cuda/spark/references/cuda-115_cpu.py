"""Independent CPU reference with deterministic contract assertions."""

plan = [("scan", "CPU"), ("filter", "GPU"), ("aggregate", "GPU"), ("collect", "CPU")]
transitions = sum(plan[i][1] != plan[i - 1][1] for i in range(1, len(plan)))
assert transitions == 2
assert sum(device == "GPU" for _, device in plan) == 2
print("Synthetic plan worksheet:", transitions, "CPU/GPU transitions")

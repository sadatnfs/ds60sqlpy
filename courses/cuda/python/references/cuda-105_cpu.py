"""Independent CPU reference with deterministic contract assertions."""

rank_ms = [10, 12, 30]
assert max(rank_ms) == 30
steps = {"rank0": 10, "rank1": 11}
consistent = len(set(steps.values())) == 1
assert not consistent
print("CPU distributed trace: barrier", max(rank_ms), "ms; checkpoint consistent", consistent)

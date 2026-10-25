"""Independent CPU reference with deterministic contract assertions."""

events = [("prepare", 0, 6), ("gpu", 2, 10)]
summed = sum(end - start for _, start, end in events)
wall = max(end for _, _, end in events) - min(start for _, start, _ in events)
assert summed == 14 and wall == 10
print("CPU timeline analysis:", summed, wall)

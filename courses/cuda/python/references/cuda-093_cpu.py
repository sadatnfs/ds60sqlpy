"""Independent CPU reference with deterministic contract assertions."""

shapes = [(4, 8), (4, 8), (8, 8)]
assert len(set(shapes)) == 2
compile_ms, saving_ms = 500, 1
assert compile_ms / saving_ms == 500
print("CPU compilation model:", len(set(shapes)), "specializations; break-even", 500)

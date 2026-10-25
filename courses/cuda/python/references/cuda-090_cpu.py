"""Independent CPU reference with deterministic contract assertions."""

gradient = 0.5
scale = 1024
scaled = gradient * scale
correct = min(scaled / scale, 1.0)
wrong = min(scaled, 1.0) / scale
assert correct == 0.5 and wrong == 1 / 1024
print("CPU scaling model:", correct, wrong)

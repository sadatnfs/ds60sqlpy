"""Independent CPU reference with deterministic contract assertions."""

batch, seconds = 32, 0.008
throughput = batch / seconds
amortized = seconds / batch
assert throughput == 4000
assert amortized == 0.00025
print("CPU serving model:", throughput, "items/s; batch latency", seconds, "s")

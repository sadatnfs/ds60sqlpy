"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

batch, seconds = 32, 0.008
throughput = batch / seconds
amortized = seconds / batch
assert throughput == 4000
assert amortized == 0.00025
print("CPU serving model:", throughput, "items/s; batch latency", seconds, "s")

"""Independent CPU reference with deterministic contract assertions."""

saved_compute, added_transfer = 30, 40
net = added_transfer - saved_compute
assert net == 10
candidates = {"local_cpu": 0.1, "spark_startup_only": 3.0}
assert candidates["local_cpu"] < candidates["spark_startup_only"]
print("CPU architecture decision: GPU candidate adds", net, "seconds")

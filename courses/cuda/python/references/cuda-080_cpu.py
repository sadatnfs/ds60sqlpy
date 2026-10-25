"""Independent CPU reference with deterministic contract assertions."""

serial_counter = 0
for _ in range(2):
    serial_counter += 1
parallel_reads = [0, 0]
lost_update = max(value + 1 for value in parallel_reads)
assert serial_counter == 2 and lost_update == 1
print("CPU race illustration:", serial_counter, lost_update)

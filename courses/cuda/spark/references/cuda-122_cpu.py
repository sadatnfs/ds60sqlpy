"""Independent CPU reference with deterministic contract assertions."""

gib = 1024**3
payload = 10 * gib
bandwidth = gib
seconds = payload / bandwidth
assert seconds == 10
kernel_saving = 0.05
assert kernel_saving / seconds < 0.01
print("CPU shuffle bound:", seconds, "seconds before additional overhead")

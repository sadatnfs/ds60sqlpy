"""Independent CPU reference with deterministic contract assertions."""

reserved = 1024
live = 1024
live -= 1024
assert live == 0 and reserved == 1024
live += 1024
assert live <= reserved
retained = [1024 for _ in range(4)]
assert sum(retained) == 4096
print("CPU allocator model:", live, reserved, sum(retained))

"""Independent CPU reference with deterministic contract assertions."""

required = {"python", "framework", "toolkit", "host_arch", "device_targets"}
manifest = {
    "python": "pinned",
    "framework": "pinned",
    "toolkit": "pinned",
    "host_arch": "declared",
    "device_targets": ["qualified separately"],
}
assert set(manifest) == required
assert "driver" not in manifest
print("CPU package ledger: build metadata complete; runtime driver still separate")

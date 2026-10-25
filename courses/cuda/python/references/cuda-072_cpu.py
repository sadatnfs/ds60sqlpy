"""Independent CPU reference with deterministic contract assertions."""

stages = ["import", "visibility", "allocation", "launch", "completion", "correctness"]
observed = {name: True for name in stages}
observed["correctness"] = False
assert not all(observed.values())
failed = next(name for name in stages if not observed[name])
assert failed == "correctness"
print("CPU diagnostic fixture: failed at", failed)

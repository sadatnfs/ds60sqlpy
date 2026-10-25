"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

stages = ["import", "visibility", "allocation", "launch", "completion", "correctness"]
observed = {name: True for name in stages}
observed["correctness"] = False
assert not all(observed.values())
failed = next(name for name in stages if not observed[name])
assert failed == "correctness"
print("CPU diagnostic fixture: failed at", failed)

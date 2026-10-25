"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

states = [
    {"gpu_visible": False, "plugin_enabled": False},
    {"gpu_visible": True, "plugin_enabled": True, "cpu_operator": True},
]
assert states[0]["plugin_enabled"] is False
assert states[1]["cpu_operator"] is True
print("CPU configuration worksheet: CPU baseline and GPU mixed plan are distinct")

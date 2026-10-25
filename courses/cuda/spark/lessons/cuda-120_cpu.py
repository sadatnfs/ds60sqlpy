"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

per_task, shared, capacity = 2, 1, 8
assert 3 * per_task + shared == 7
assert 4 * per_task + shared == 9
safe = [tasks for tasks in range(1, 5) if tasks * per_task + shared <= capacity]
assert safe == [1, 2, 3]
print("CPU memory budget:", safe, "safe task counts in the model")

"""cuda-014: CPU reference only, not CUDA execution."""

n, stride = 19, 8
owners = [list(range(t, n, stride)) for t in range(stride)]
flat = [i for group in owners for i in group]
assert sorted(flat) == list(range(n)) and len(set(flat)) == n
assert owners[0] == [0, 8, 16]
print({"thread_0": owners[0], "all_elements_written_once": True})

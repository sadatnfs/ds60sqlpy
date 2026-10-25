"""cuda-020: CPU reference only, not CUDA execution."""

values = [1, 2, 3, 4, 5, 0, 0, 0]
width = len(values) // 2
trace = []
while width:
    for i in range(width):
        values[i] += values[i + width]
    trace.append(values[:width])
    width //= 2
assert trace == [[6, 2, 3, 4], [9, 6], [15]]
print(trace)

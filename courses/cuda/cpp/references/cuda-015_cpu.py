"""cuda-015: CPU reference only, not CUDA execution."""

width, height, stride = 3, 2, 4
image = [1, 2, 3, 99, 4, 5, 6, 99]
for row in range(height):
    for col in range(width):
        image[row * stride + col] += 10
assert image == [11, 12, 13, 99, 14, 15, 16, 99]
print(image)

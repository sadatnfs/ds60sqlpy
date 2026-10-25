"""cuda-058: CPU reference only, not CUDA execution."""

assert 1 * 3 + 2 == 5
assert 2 * 1 + 1 * 3 == 5
values = [-2, 1, 4]
correct = [max(0, x + 1) for x in values]
wrong = [max(0, x) + 1 for x in values]
assert correct == [0, 2, 5] and wrong == [1, 2, 5]
print({"correct_epilogue": correct, "changed_operation_order": wrong})

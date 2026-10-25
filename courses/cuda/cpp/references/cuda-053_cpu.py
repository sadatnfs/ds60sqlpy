"""cuda-053: CPU reference only, not CUDA execution."""

exact_input = 1.001
rounded_input = float(format(exact_input, ".3g"))
assert rounded_input == 1.0
exact_sum, quantized_sum = exact_input * 1000, rounded_input * 1000
assert abs(exact_sum - quantized_sum - 1) < 1e-9
print(
    {
        "toy_decimal_exact_sum": exact_sum,
        "toy_quantized_sum": quantized_sum,
        "tensor_core_emulation": False,
    }
)

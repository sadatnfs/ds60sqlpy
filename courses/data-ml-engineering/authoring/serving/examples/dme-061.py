"""Actual CPU placement and a separate analytical transfer/capacity budget."""

import torch


def example_one():
    torch.set_num_threads(2)
    source = torch.arange(12, dtype=torch.float32).reshape(3, 4)
    weight = torch.tensor([[1.0], [0.0], [-1.0], [2.0]])
    result = source.to("cpu") @ weight.to("cpu")
    torch.testing.assert_close(result[:, 0], torch.tensor([4.0, 12.0, 20.0]))
    assert result.device.type == "cpu"
    print("Executed device:", result.device, "result:", result[:, 0].tolist())
    print("CPU evidence does not qualify CUDA or Apple GPU execution.")


def example_two():
    parameter_count = 7_000_000_000
    weights = parameter_count * 2
    bandwidth_bytes_per_second = 25_000_000_000
    theoretical_transfer_seconds = weights / bandwidth_bytes_per_second
    assert abs(theoretical_transfer_seconds - 0.56) < 1e-12
    layers, heads, head_width, tokens, bytes_per_element = 32, 8, 128, 4096, 2
    kv = 2 * layers * heads * head_width * tokens * bytes_per_element
    assert kv == 536_870_912
    print("Hypothetical lower-bound transfer seconds:", theoretical_transfer_seconds)
    print("Hypothetical per-request KV GiB:", kv / 2**30)
    print(
        "Allocator state, temporary tensors, driver reservations and "
        "synchronization need separate budgets."
    )


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()

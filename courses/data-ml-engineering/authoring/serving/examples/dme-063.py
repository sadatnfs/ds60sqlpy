"""Real Torch attention: prefill and one-token cached decode must agree."""

import math

import torch
import torch.nn.functional as functional


def fixture():
    generator = torch.Generator().manual_seed(11)
    return [torch.randn((1, 2, 5, 4), generator=generator) for _ in range(3)]


def example_one():
    query, key, value = fixture()
    full = functional.scaled_dot_product_attention(query, key, value, is_causal=True, dropout_p=0.0)
    pieces = []
    for end in range(1, 6):
        part = functional.scaled_dot_product_attention(
            query[:, :, end - 1 : end],
            key[:, :, :end],
            value[:, :, :end],
            is_causal=False,
            dropout_p=0.0,
        )
        pieces.append(part)
    cached = torch.cat(pieces, dim=2)
    torch.testing.assert_close(cached, full, rtol=1e-5, atol=1e-6)
    wrong = functional.scaled_dot_product_attention(
        query[:, :, -1:], key, value, is_causal=True, dropout_p=0.0
    )
    assert not torch.allclose(wrong, full[:, :, -1:])
    print("Full/cached max error:", float((full - cached).abs().max()))
    print("A rectangular top-left causal mask is wrong for this single cached query.")


def example_two():
    query, key, value = fixture()
    scores = query @ key.transpose(-2, -1) / math.sqrt(4)
    mask = torch.ones((5, 5), dtype=torch.bool).tril()
    manual = torch.softmax(scores.masked_fill(~mask, -torch.inf), dim=-1) @ value
    expected = functional.scaled_dot_product_attention(
        query, key, value, is_causal=True, dropout_p=0.0
    )
    torch.testing.assert_close(manual, expected, rtol=1e-5, atol=1e-6)
    changed = value.clone()
    changed[:, :, -1] += 1000
    altered = functional.scaled_dot_product_attention(
        query, key, changed, is_causal=True, dropout_p=0.0
    )
    torch.testing.assert_close(altered[:, :, :-1], expected[:, :, :-1], rtol=0, atol=0)
    print("Independent softmax formula and future-token perturbation both passed on CPU.")


def main():
    torch.set_num_threads(2)
    example_one()
    example_two()


if __name__ == "__main__":
    main()

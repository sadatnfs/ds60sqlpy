"""Paged-cache accounting and copy-on-write ownership as an explicit CPU model."""

import math


def cache_bytes(layers, kv_heads, width, tokens, element_bytes=2):
    return 2 * layers * kv_heads * width * tokens * element_bytes


def example_one():
    lengths = [5, 9, 15]
    page = 4
    allocated = sum(math.ceil(length / page) * page for length in lengths)
    assert allocated == 36 and sum(lengths) == 29
    reserved = len(lengths) * 32
    assert reserved == 96
    print("Used tokens", sum(lengths), "page slots", allocated, "fixed maximum slots", reserved)
    assert cache_bytes(32, 8, 128, 4096) == 2**29
    print("32-layer grouped-query KV GiB:", cache_bytes(32, 8, 128, 4096) / 2**30)


def example_two():
    pages = {0: [10, 11, 12, 13], 1: [14, 15]}
    mappings = {"a": [0, 1], "b": [0, 1]}
    refs = {0: 2, 1: 2}
    old = mappings["b"][-1]
    new = max(pages) + 1
    pages[new] = pages[old].copy()
    refs[old] -= 1
    refs[new] = 1
    mappings["b"][-1] = new
    pages[new].append(99)
    assert pages[1] == [14, 15] and pages[2] == [14, 15, 99]
    assert mappings == {"a": [0, 1], "b": [0, 2]}
    assert refs == {0: 2, 1: 1, 2: 1}
    print("Prefix-sharing maps", mappings, "reference counts", refs)
    print("A page table alone does not execute paged attention on a GPU.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()

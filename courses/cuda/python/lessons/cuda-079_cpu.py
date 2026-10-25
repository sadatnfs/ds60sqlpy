"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def segments(offsets, width=32):
    return len({offset // width for offset in offsets})


contiguous = [4 * i for i in range(8)]
strided = [32 * i for i in range(8)]
assert segments(contiguous) == 1 and segments(strided) == 8
print("CPU segment model:", segments(contiguous), segments(strided))

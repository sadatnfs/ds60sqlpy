"""Independent CPU reference with deterministic contract assertions."""


def segments(offsets, width=32):
    return len({offset // width for offset in offsets})


contiguous = [4 * i for i in range(8)]
strided = [32 * i for i in range(8)]
assert segments(contiguous) == 1 and segments(strided) == 8
print("CPU segment model:", segments(contiguous), segments(strided))

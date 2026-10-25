"""cuda-059: answer-free CPU model practice."""

# CPU model practice: PTX, SASS, JIT and inspecting generated code
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Distinguish native image compatibility from
# PTX JIT compatibility.
# Check the boundary from Exercise 5: What should an unsupported target diagnostic
# change?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

artifacts = {
    "source.cu": "CUDA C++ source",
    "kernel.ptx": "virtual instructions",
    "kernel.cubin": "target machine code",
    "main": "host executable",
}

raise NotImplementedError("Implement the CPU model and boundary assertions above.")

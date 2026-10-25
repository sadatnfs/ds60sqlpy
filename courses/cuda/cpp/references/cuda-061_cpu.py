"""cuda-061: CPU reference only, not CUDA execution."""

project = {
    "include/transform.hpp": "host interface",
    "src/transform.cu": "kernel and launcher",
    "src/main.cpp": "fixture and validation",
    "build/": "generated artifacts",
}
assert len(project) == 4
print(project)

# CUDA through Python, with equal PyTorch and TensorFlow lanes

This route contains `cuda-065` through `cuda-112`. Begin after the shared GPU
foundations, or enter the machine-learning branch at `cuda-087` after reviewing
its direct prerequisites. You do not need to finish advanced C++ to start
Python array or framework work.

Every chapter has a reading worksheet, six targeted exercises, progressive
hints, separate explained answers and an editable **CPU reference model**. The
CPU programs use only the standard library and small synthetic fixtures. They
teach arithmetic, indexing, ownership and evidence contracts without claiming
to execute or accurately simulate a GPU.

Seven chapters include a separately prepared CuPy CUDA variant. Ten ML chapters
include both PyTorch and TensorFlow programs, each with explicit CPU and NVIDIA
CUDA variants. These examples cover training, input pipelines, memory,
convolution, restart state, inference, gradients, accumulation, attention and
adapters. CPU versions force CPU placement. CUDA versions fail clearly when the
required NVIDIA backend is unavailable; they never silently substitute CPU.

The ordinary Docker classroom works on Linux, macOS and Windows through WSL 2.
An Apple GPU cannot execute CUDA. Native PyTorch MPS, supported AMD ROCm setups,
and other vendor backends are distinct optional learning environments with
separate package, device and operation qualification. Native Mac MPS is not
exposed automatically through the ordinary Linux Docker worker.

Advanced multi-host training, custom compiled operators, kernel DSLs and
inference engines are complete reading/design workshops with explicitly
prepared external runtime requirements. They do not imply arbitrary multi-file
builds or package downloads from a classroom pad. No chapter downloads a model
or dataset when opened.

Use [the platform guide](platforms.md) to choose a truthful execution route and
[the framework guide](framework-lanes.md) to compare PyTorch and TensorFlow.
The [GPU Spark specialization](../spark/README.md) is a separate branch and can
start after common GPU foundations plus the existing Spark lessons.

A [maintained numba-cuda example](manual/numba_affine.py) is also provided as an
explicit external lab. It is not part of the CuPy-only worker dependency set.
Prepare a release-compatible `numba-cuda` environment on an owned NVIDIA host,
then run it there. It rejects the old unqualified distribution assumption,
missing CUDA capability and simulator mode, and checks singleton and tail cases.
No claim of actual device execution is made merely because the file parses.

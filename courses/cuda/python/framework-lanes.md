# PyTorch and TensorFlow GPU practice

Both frameworks can execute supported operations on NVIDIA CUDA devices when
installed in compatible, explicitly prepared environments. Keep their workers
and dependency sets separate. Ordinary `llm-torch-cpu` and `tensorflow-cpu`
remain CPU teaching profiles; installing those does not enable CUDA by itself.

The shared chapters derive the same mathematics before introducing each
framework's idioms. Ten chapters contain complete parallel implementation lanes:

| Chapter | PyTorch mechanism | TensorFlow mechanism |
| --- | --- | --- |
| `cuda-087` | Parameter, mean loss, backward, SGD | Variable, GradientTape, mean loss, SGD |
| `cuda-088` | Bounded DataLoader and explicit device transfer | Finite tf.data batch/prefetch and explicit placement |
| `cuda-089` | Logical tensor bytes, allocated/reserved distinction | Logical tensor bytes and allocator observation |
| `cuda-091` | Conv1d NCL cross-correlation | Conv1d NLC cross-correlation |
| `cuda-094` | Weight and optimizer state restore | Explicit weight and momentum-variable restore |
| `cuda-095` | eval plus inference_mode | Explicit training=False |
| `cuda-098` | Autograd plus gradcheck | GradientTape plus finite differences |
| `cuda-099` | Example-weighted microbatch accumulation | Example-weighted tape gradient accumulation |
| `cuda-100` | Explicit attention compared with supported attention API | Explicit masked softmax/matmul attention reference |
| `cuda-101` | Frozen base and low-rank trainable parameters | Nontrainable base variable and low-rank trainable variables |

Each chapter offers CPU and NVIDIA CUDA versions. They use small synthetic data,
no pretrained model downloads, and explicit device selection. They are editable
worked examples, not solutions to every reasoning exercise. The reference copies
include assertions and belong to the separate solution area.

The remaining ML chapters develop precision policy, profiling, compilation,
capstone reporting, KV caches and distributed systems in detail. Their framework
sections explain the appropriate APIs and acceptance tests. A custom operator,
compiled model, engine or distributed training job requires the separately
prepared workflow stated in that chapter; a single-file classroom pad does not
imply that those toolchains or infrastructure exist.

The restart examples deliberately restore numerical state in memory. They do
not export a persistent training checkpoint or snapshot a live GPU context.
A durable external project must additionally save all relevant optimizer,
scaler, RNG and data-position state to storage that outlives the process, then
exercise actual process restart and reload.

The attention examples teach equivalent mathematical contracts, not identical
kernel selection. The TensorFlow reference does not claim a fused attention
backend; the PyTorch API call does not by itself prove which optimized backend
was selected. Inspect real device traces before making those performance claims.

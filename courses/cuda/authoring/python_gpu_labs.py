"""Small opt-in CUDA labs. Hardware-required programs never fall back silently."""

CUPY = {
    1: """x = cp.asarray([1.0, 2.0, 3.0], dtype=cp.float32)
y = cp.sum(x)
cp.cuda.get_current_stream().synchronize()
assert float(y.get()) == 6.0
print("CUDA array sum:", float(y.get()), "device", x.device.id)""",
    2: """x = cp.arange(6, dtype=cp.float32).reshape(2, 3)
view = x[:, ::2]
assert view.shape == (2, 2)
assert view.strides == (12, 8)
cp.testing.assert_array_equal(view, cp.asarray([[0, 2], [3, 5]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA layout:", view.shape, view.strides, cp.asnumpy(view).tolist())""",
    4: """x = cp.asarray([[1.0, 3.0], [3.0, 7.0]], dtype=cp.float32)
centered = x - cp.mean(x, axis=0)
cp.testing.assert_allclose(centered, cp.asarray([[-1, -2], [1, 2]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA centered features:", cp.asnumpy(centered).tolist())""",
    7: """x = cp.arange(4096, dtype=cp.float32)
for _ in range(2):
    y = x * 2 + 1
cp.cuda.get_current_stream().synchronize()
start, end = cp.cuda.Event(), cp.cuda.Event()
start.record()
y = x * 2 + 1
end.record()
end.synchronize()
cp.testing.assert_allclose(y, 2 * cp.arange(4096, dtype=cp.float32) + 1)
print("CUDA event interval:", cp.cuda.get_elapsed_time(start, end), "ms; excludes transfers and initial compilation")""",
    10: '''kernel = cp.RawKernel(r"""
extern "C" __global__ void twice(const float* x, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = 2.0f * x[i];
}
""", "twice")
for n in [0, 1, 127, 128, 129, 257]:
    x = cp.arange(n, dtype=cp.float32)
    y = cp.empty_like(x)
    if n:
        kernel(((n + 127) // 128,), (128,), (x, y, cp.int32(n)))
    cp.cuda.get_current_stream().synchronize()
    cp.testing.assert_array_equal(y, 2 * x)
print("CUDA tail tests passed for zero, singleton and nonmultiples")''',
    13: """values = [1.0, 2.0, 3.0, 4.0, 5.0]
x = cp.asarray(values, dtype=cp.float64)
result = float(cp.sum(x).get())
assert math.isclose(result, math.fsum(values), rel_tol=1e-12, abs_tol=1e-12)
cp.cuda.get_current_stream().synchronize()
print("CUDA library reduction:", result, "; order-sensitive cases need a documented tolerance")""",
    20: '''kernel = cp.RawKernel(r"""
extern "C" __global__ void affine(const float* x, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = 2.0f * x[i] + 1.0f;
}
""", "affine")
x = cp.asarray([-1.0, 0.0, 3.0], dtype=cp.float32)
y = cp.empty_like(x)
kernel((1,), (128,), (x, y, cp.int32(x.size)))
cp.cuda.get_current_stream().synchronize()
cp.testing.assert_allclose(y, cp.asarray([-1.0, 1.0, 7.0], dtype=cp.float32))
print("CUDA raw affine:", cp.asnumpy(y).tolist())''',
}

# CPU and CUDA copies are generated from the same arithmetic body. Device setup
# is explicit, so CUDA variants cannot quietly turn into CPU demonstrations.
TORCH = {
    23: """x = torch.tensor([1.0, 2.0], device=device)
y = torch.tensor([2.0, 4.0], device=device)
w = torch.tensor(0.0, device=device, requires_grad=True)
optimizer = torch.optim.SGD([w], lr=0.1)
loss = ((w*x-y)**2).mean()
loss.backward()
assert torch.allclose(w.grad, torch.tensor(-10.0, device=device))
optimizer.step()
assert torch.allclose(w, torch.tensor(1.0, device=device))
print("PyTorch one-step weight:", float(w.detach().cpu()), "device", w.device)""",
    24: """x = torch.arange(8, dtype=torch.float32).reshape(4, 2)
loader = DataLoader(TensorDataset(x), batch_size=2, shuffle=False, num_workers=0, pin_memory=(device.type == "cuda"))
observed = []
for (batch,) in loader:
    values = batch.to(device, non_blocking=(device.type == "cuda"))
    observed.extend(values.sum(dim=1).cpu().tolist())
assert observed == [1.0, 5.0, 9.0, 13.0]
print("PyTorch bounded input pipeline:", observed)""",
    25: """x = torch.ones((8, 16), device=device, requires_grad=True)
loss = x.square().mean()
loss.backward()
logical_bytes = x.numel() * x.element_size()
assert logical_bytes == 512
assert x.grad is not None and torch.isfinite(x.grad).all()
print("PyTorch input payload:", logical_bytes, "bytes; excludes gradients, context and reserve")
if device.type == "cuda":
    torch.cuda.synchronize()
    print("Allocated:", torch.cuda.memory_allocated(), "reserved:", torch.cuda.memory_reserved())""",
    27: """x = torch.tensor([1.0, 2.0, 3.0, 4.0], device=device).reshape(1, 1, 4)
kernel = torch.tensor([1.0, -1.0], device=device).reshape(1, 1, 2)
y = torch.nn.functional.conv1d(x, kernel)
assert torch.allclose(y, torch.full((1, 1, 3), -1.0, device=device))
print("PyTorch cross-correlation:", y.cpu().tolist())""",
    30: """w = torch.nn.Parameter(torch.tensor(1.0, device=device))
optimizer = torch.optim.SGD([w], lr=0.1, momentum=0.9)
for _ in range(2):
    optimizer.zero_grad()
    w.square().backward()
    optimizer.step()
saved_weight = w.detach().clone()
saved_optimizer = copy.deepcopy(optimizer.state_dict())
optimizer.zero_grad()
w.square().backward()
optimizer.step()
expected = w.detach().clone()
with torch.no_grad():
    w.copy_(saved_weight)
optimizer.load_state_dict(saved_optimizer)
optimizer.zero_grad()
w.square().backward()
optimizer.step()
assert torch.allclose(w, expected)
print("PyTorch in-memory checkpoint continuation:", float(w.detach().cpu()))""",
    31: """model = torch.nn.Sequential(torch.nn.Linear(2, 1, bias=False), torch.nn.Dropout(0.5)).to(device)
with torch.no_grad():
    model[0].weight.copy_(torch.tensor([[2.0, -1.0]], device=device))
model.eval()
with torch.inference_mode():
    y = model(torch.tensor([[1.0, 3.0], [2.0, 1.0]], device=device))
assert torch.allclose(y, torch.tensor([[-1.0], [3.0]], device=device))
print("PyTorch evaluation output:", y.cpu().tolist())""",
    34: """x = torch.tensor([2.0, -2.0], dtype=torch.float64, device=device, requires_grad=True)
y = torch.relu(2*x+1).sum()
y.backward()
assert torch.allclose(x.grad, torch.tensor([2.0, 0.0], dtype=torch.float64, device=device))
assert torch.autograd.gradcheck(lambda z: torch.relu(2*z+1), (x.detach().requires_grad_(),))
print("PyTorch gradient reference:", x.grad.cpu().tolist())""",
    35: """x = torch.tensor([1.0, 2.0, 3.0, 4.0], device=device)
y = 2*x
full = torch.tensor(0.0, device=device, requires_grad=True)
((full*x-y)**2).mean().backward()
small = torch.tensor(0.0, device=device, requires_grad=True)
for a, b in [(x[:3], y[:3]), (x[3:], y[3:])]:
    (((small*a-b)**2).sum()/x.numel()).backward()
assert torch.allclose(full.grad, small.grad)
print("PyTorch unequal microbatch gradient:", float(small.grad.cpu()))""",
    36: """q = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]], device=device)
k = q.clone()
v = torch.tensor([[[[2.0, 3.0], [4.0, 5.0]]]], device=device)
scores = q @ k.transpose(-2, -1) / (2**0.5)
mask = torch.ones((2, 2), dtype=torch.bool, device=device).tril()
reference = torch.softmax(scores.masked_fill(~mask, float("-inf")), dim=-1) @ v
actual = torch.nn.functional.scaled_dot_product_attention(q, k, v, is_causal=True)
assert torch.allclose(actual, reference, atol=1e-5, rtol=1e-5)
print("PyTorch attention parity:", actual.cpu().tolist(), "; selected kernel backend not inferred")""",
    37: """base = torch.eye(4, device=device)
base.requires_grad_(False)
a = torch.nn.Parameter(torch.ones((4, 1), device=device)*0.1)
b = torch.nn.Parameter(torch.zeros((1, 4), device=device))
x = torch.ones((2, 4), device=device)
optimizer = torch.optim.SGD([a, b], lr=0.1)
loss = (x @ (base+a@b)).square().mean()
loss.backward()
optimizer.step()
assert base.grad is None
assert a.numel()+b.numel() == 8 and base.numel() == 16
assert torch.isfinite(a).all() and torch.isfinite(b).all()
print("PyTorch adapter census: base 16 frozen; trainable 8; base storage remains")""",
}

TENSORFLOW = {
    23: """with tf.device(device):
    x = tf.constant([1.0, 2.0])
    y = tf.constant([2.0, 4.0])
    w = tf.Variable(0.0)
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.1)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(w*x-y))
    gradient = tape.gradient(loss, w)
    tf.debugging.assert_near(gradient, tf.constant(-10.0))
    optimizer.apply_gradients([(gradient, w)])
    tf.debugging.assert_near(w, tf.constant(1.0))
print("TensorFlow one-step weight:", float(w.numpy()), "device", w.device)""",
    24: """dataset = tf.data.Dataset.from_tensor_slices(tf.reshape(tf.range(8, dtype=tf.float32), (4, 2))).batch(2).prefetch(1)
options = tf.data.Options()
options.threading.private_threadpool_size = 1
dataset = dataset.with_options(options)
observed = []
for batch in dataset:
    with tf.device(device):
        values = tf.identity(batch)
        observed.extend(tf.reduce_sum(values, axis=1).numpy().tolist())
assert observed == [1.0, 5.0, 9.0, 13.0]
print("TensorFlow bounded input pipeline:", observed)""",
    25: """with tf.device(device):
    x = tf.Variable(tf.ones((8, 16)))
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(x))
    gradient = tape.gradient(loss, x)
    tf.debugging.assert_all_finite(gradient, "gradient must be finite")
logical_bytes = int(tf.size(x).numpy()) * x.dtype.size
assert logical_bytes == 512
print("TensorFlow input payload:", logical_bytes, "bytes; excludes gradient, context and reserve")
if device == "/GPU:0":
    print("TensorFlow allocator snapshot:", tf.config.experimental.get_memory_info("GPU:0"))""",
    27: """with tf.device(device):
    x = tf.reshape(tf.constant([1.0, 2.0, 3.0, 4.0]), (1, 4, 1))
    kernel = tf.reshape(tf.constant([1.0, -1.0]), (2, 1, 1))
    y = tf.nn.conv1d(x, kernel, stride=1, padding="VALID")
    tf.debugging.assert_near(y, tf.fill((1, 3, 1), -1.0))
print("TensorFlow cross-correlation:", y.numpy().tolist())""",
    30: """with tf.device(device):
    w = tf.Variable(1.0)
    velocity = tf.Variable(0.0)
    def step():
        with tf.GradientTape() as tape:
            loss = tf.square(w)
        gradient = tape.gradient(loss, w)
        velocity.assign(0.9*velocity+gradient)
        w.assign_sub(0.1*velocity)
    step()
    step()
    saved_weight, saved_velocity = tf.identity(w), tf.identity(velocity)
    step()
    expected = tf.identity(w)
    w.assign(saved_weight)
    velocity.assign(saved_velocity)
    step()
    tf.debugging.assert_near(w, expected)
print("TensorFlow in-memory momentum continuation:", float(w.numpy()))""",
    31: """with tf.device(device):
    model = tf.keras.Sequential([tf.keras.layers.Input(shape=(2,)), tf.keras.layers.Dense(1, use_bias=False), tf.keras.layers.Dropout(0.5)])
    model.layers[0].set_weights([tf.constant([[2.0], [-1.0]]).numpy()])
    y = model(tf.constant([[1.0, 3.0], [2.0, 1.0]]), training=False)
    tf.debugging.assert_near(y, tf.constant([[-1.0], [3.0]]))
print("TensorFlow evaluation output:", y.numpy().tolist())""",
    34: """with tf.device(device):
    x = tf.Variable([2.0, -2.0], dtype=tf.float64)
    with tf.GradientTape() as tape:
        y = tf.reduce_sum(tf.nn.relu(2*x+1))
    gradient = tape.gradient(y, x)
    tf.debugging.assert_near(gradient, tf.constant([2.0, 0.0], dtype=tf.float64))
    eps = tf.constant(1e-5, dtype=tf.float64)
    numeric = (tf.nn.relu(2*(x+eps)+1)-tf.nn.relu(2*(x-eps)+1))/(2*eps)
    tf.debugging.assert_near(gradient, numeric, atol=1e-8, rtol=1e-8)
print("TensorFlow gradient reference:", gradient.numpy().tolist())""",
    35: """with tf.device(device):
    x = tf.constant([1.0, 2.0, 3.0, 4.0])
    y = 2*x
    w = tf.Variable(0.0)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(w*x-y))
    full = tape.gradient(loss, w)
    accumulated = tf.constant(0.0)
    for a, b in [(x[:3], y[:3]), (x[3:], y[3:])]:
        with tf.GradientTape() as tape:
            micro_loss = tf.reduce_sum(tf.square(w*a-b))/4.0
        accumulated += tape.gradient(micro_loss, w)
    tf.debugging.assert_near(full, accumulated)
print("TensorFlow unequal microbatch gradient:", float(accumulated.numpy()))""",
    36: """with tf.device(device):
    q = tf.constant([[[1.0, 0.0], [0.0, 1.0]]])
    k = tf.identity(q)
    v = tf.constant([[[2.0, 3.0], [4.0, 5.0]]])
    scores = tf.matmul(q, k, transpose_b=True)/tf.sqrt(2.0)
    mask = tf.linalg.band_part(tf.ones((2, 2), dtype=tf.int32), -1, 0)>0
    masked = tf.where(mask, scores, tf.constant(float("-inf")))
    weights = tf.nn.softmax(masked, axis=-1)
    actual = tf.matmul(weights, v)
    tf.debugging.assert_near(actual[:, 0, :], v[:, 0, :])
    tf.debugging.assert_near(tf.reduce_sum(weights, axis=-1), tf.ones((1, 2)))
print("TensorFlow causal attention:", actual.numpy().tolist(), "; no fused-backend claim")""",
    37: """with tf.device(device):
    base = tf.Variable(tf.eye(4), trainable=False)
    a = tf.Variable(tf.ones((4, 1))*0.1)
    b = tf.Variable(tf.zeros((1, 4)))
    x = tf.ones((2, 4))
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.1)
    with tf.GradientTape() as tape:
        loss = tf.reduce_mean(tf.square(tf.matmul(x, base+tf.matmul(a, b))))
    gradients = tape.gradient(loss, [a, b])
    optimizer.apply_gradients(zip(gradients, [a, b], strict=True))
    tf.debugging.assert_all_finite(a, "a finite")
    tf.debugging.assert_all_finite(b, "b finite")
assert int(tf.size(a).numpy()+tf.size(b).numpy()) == 8
assert int(tf.size(base).numpy()) == 16
print("TensorFlow adapter census: base 16 frozen; trainable 8; base storage remains")""",
}


def cupy_program(n):
    header = '"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""\n\n'
    if n == 13:
        header += "import math\n\n"
    header += "import cupy as cp\n\n"
    header += 'if cp.cuda.runtime.getDeviceCount() < 1:\n    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")\ncp.cuda.Device(0).use()\n'
    return header + "\n" + CUPY[n].strip() + "\n"


def torch_program(n, gpu):
    header = '"""Bounded PyTorch lesson with explicit execution device."""\n\n'
    if n == 30:
        header += "import copy\n\n"
    header += "import torch\n"
    if n == 24:
        header += "from torch.utils.data import DataLoader, TensorDataset\n"
    header += "\ntorch.set_num_threads(1)\n"
    if gpu:
        header += 'if not torch.cuda.is_available() or torch.version.hip is not None:\n    raise RuntimeError("This variant requires NVIDIA CUDA, not CPU or ROCm fallback")\ndevice = torch.device("cuda:0")\n'
    else:
        header += 'device = torch.device("cpu")\n'
    return header + "\n" + TORCH[n].strip() + "\n" + ("torch.cuda.synchronize()\n" if gpu else "")


def tensorflow_program(n, gpu):
    header = '"""Bounded TensorFlow lesson with explicit execution device."""\nimport tensorflow as tf\n\ntf.config.threading.set_inter_op_parallelism_threads(1)\ntf.config.threading.set_intra_op_parallelism_threads(1)\n'
    if gpu:
        header += 'if not tf.test.is_built_with_cuda() or not tf.config.list_physical_devices("GPU"):\n    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")\nfor gpu_device in tf.config.list_physical_devices("GPU"):\n    tf.config.experimental.set_memory_growth(gpu_device, True)\ndevice = "/GPU:0"\n'
    else:
        header += 'tf.config.set_visible_devices([], "GPU")\ndevice = "/CPU:0"\n'
    checked = {
        23: "w",
        24: "values",
        25: "loss",
        27: "y",
        30: "w",
        31: "y",
        34: "gradient",
        35: "accumulated",
        36: "actual",
        37: "loss",
    }[n]
    tail = (
        f'assert "GPU" in {checked}.device.upper(), "Expected actual GPU placement"\n'
        if gpu
        else ""
    )
    return header + "\n" + TENSORFLOW[n].strip() + "\n" + tail

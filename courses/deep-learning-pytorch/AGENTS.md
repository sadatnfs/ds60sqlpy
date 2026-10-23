# PyTorch authoring contract

The user wants PyTorch and TensorFlow in equally large amounts, with very
detailed explanations. This is a complete36lesson deep-learning route, not
only the PyTorch snippets inside LLM theory. Read root guidance and the paired
TensorFlow guide before authoring each topic. No em dashes. Use original prose.

Teach PyTorch idioms rather than mechanically renaming TensorFlow APIs. Explain
notation, tensor shapes/dtypes/devices, gradient flow, parameter and buffer
registration, training/evaluation state, optimizer membership and failure modes.
Use3worked examples where practical, six distinct inspectable exercises,
progressive hints, separate learner/reference/explained solutions, and answered
interview reasoning. Compare the equivalent TensorFlow operation explicitly,
including different defaults, layouts, reductions and state behavior.

Use the existing llm-torch-cpu worker as the prepared PyTorch CPU runtime.
Its current dependency lock is PyTorch2.9.1 CPU and NumPy2.2.6, with no sklearn,
torchvision, external datasets or pretrained weights assumed. The profile's
historical name does not restrict it to LLMs. New runtime registration is not
needed. The first reading lesson uses reading/markdown; other lessons run as
main.py in an isolated temporary job directory. No GPU is assumed.

Keep examples small, offline and deterministic. DataLoader defaults to
num_workers=0 in the classroom, with explicit separate process/device guidance.
Do not call a CPU arithmetic demonstration a multi-GPU scalability proof or a
QLoRA deployment. Real checkpoint/export tests must use a fresh subprocess,
include its stderr on failure, preserve state ownership and bound cleanup.
Use weights_only=True for suitable local checkpoint formats and explain the
artifact contract. Consult versioned2.9documentation for supported APIs.

Register complete authored sets only in lessons.json. Keep paired_lesson_id
metadata and relative TensorFlow guide links aligned. Write focused tests in
tests/test_pytorch_lessons.py and status in docs/implementation/pytorch-content-status.md.
Root owns shared runtime/Compose files, actual Docker and browser qualification.

# PyTorch authoring contract

Maintain comparable teaching depth across the paired PyTorch and TensorFlow
routes. This subject teaches the full framework workflow, beyond the focused
PyTorch examples in LLM theory. Read root guidance and the paired
TensorFlow guide before authoring each topic. No em dashes. Use original prose.

Teach PyTorch idioms rather than mechanically renaming TensorFlow APIs. Explain
notation, tensor shapes/dtypes/devices, gradient flow, parameter and buffer
registration, training/evaluation state, optimizer membership and failure modes.
Use three worked examples where practical, six distinct inspectable exercises,
progressive hints, separate learner/reference/explained solutions, and answered
interview reasoning. Compare the equivalent TensorFlow operation explicitly,
including different defaults, layouts, reductions and state behavior.

Use the existing llm-torch-cpu worker as the prepared PyTorch CPU runtime.
Its current dependency lock is PyTorch 2.9.1 CPU and NumPy 2.2.6, with no sklearn,
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
artifact contract. Consult versioned 2.9 documentation for supported APIs.

Register complete authored sets only in lessons.json. Keep paired_lesson_id
metadata and relative TensorFlow guide links aligned. Write focused tests in
tests/test_pytorch_lessons.py and status in docs/implementation/pytorch-content-status.md.
Changes to shared runtime or Compose files need their own execution and browser
qualification. Preserve existing source-matching receipts and report what was
actually rerun.

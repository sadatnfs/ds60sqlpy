# Inference workshop maintenance

Read root guidance, the Data and ML Engineering AGENTS.md and the add-learning-path skill. This is a separate bounded optional Docker project for serving chapters 057-072, not a new classroom runtime or public provider API. Preserve existing lesson and request IDs.

Maintain the original byte-BPE tokenizer, safe NPZ manifest contract, startup-only weight loading and independently checked cached/full inference. New tokenizer, architecture or checkpoint changes require deliberate preparation; never overwrite learner model assets during start/resume. Keep prompt bytes, accepted settings, model/tokenizer hashes and sequential event identity together.

The default is actual Torch CPU on Linux AMD64/ARM64. Do not install CUDA into ordinary images or present CPU kernel names as GPU evidence. An explicit accelerator request must fail without a real supported device probe. Advanced scheduling, paged KV, quantization and speculation demonstrations remain separate from the live FIFO implementation until actually implemented and qualified.

Bound request bytes, tokens, active reservations, subscriber buffers, events, history and files. One process owns one state directory. Completed reads never generate or rewrite. Interrupted work becomes an explicit terminal error, without automatic replay. Storage failure preserves real output and reports uncertain durability. Retain original completed bytes and use direct response-byte downloads.

Use dedicated tests/test_llm_serving* and this project's check_api.py. Test real CPU inference, Unicode/BPE, cached logits, FIFO fairness, cancellation/error release, bounded backpressure, Host/Origin/auth, exact SSE/downloads, and read-only retained history after container replacement. Use original reports for readback and fresh browser documents. Do not weaken CSP for a test harness.

The helper manages only its owned copy/project. State and credentials stay outside build context. No engine socket, registry upload, unbounded downloads, unrelated cleanup or hidden native host prerequisites. Pin minimal HTTP dependencies with hashes. Format source and test strict types; root owns shared runtime/image/CI changes and aggregate book owner owns registration/generated guides.

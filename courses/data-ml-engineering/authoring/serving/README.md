# Serving lifecycle fragment

The aggregate Data and ML Engineering book consumes chapters.json. Maintain the 16 original Markdown files and complete two-case programs here; do not hand-edit generated guides. Each program is inserted at its chapter's single worked-program marker. Chapters dme-061 and dme-063 use actual Torch CPU; all other pad mechanisms use Python Core. The separate projects/inference-service/ workshop supplies actual long-lived HTTP/SSE behavior and durable state.

Run the aggregate authoring/build.py --source-check during partial work. Full publication belongs to the aggregate owner after all 72 chapters exist. Root owns shared readers, TeX compilation, runtime catalog and release gates. Existing cross-course IDs remain stable.

Keep exact distinctions among model tokens, Unicode text, SSE events and network chunks; token versus retrieval embeddings; startup weight loading and request caches; CPU arithmetic and actual accelerator kernels; queue simulations and the implemented FIFO service. No pretrained downloads or provider accounts are required. Use bounded original fixtures, independent numerical oracles, meaningful failure cases and exact retained-state checks.

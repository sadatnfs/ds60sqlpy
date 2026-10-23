# Applied LLM authoring

Follow root AGENTS.md and the full teaching-depth contract. Keep every module self-contained with three worked examples, six concrete exercises, expected observations, progressive hints and separate reference/explanatory solutions. Preserve stable IDs and prerequistes. Never call a count, lexical, extractive or toy decoder baseline a production LLM.

Default execution is offline after deliberately prepared NumPy/PyTorch dependencies. No model or dataset download and no paid API call belongs in default code. The optional pretrained recipe separates dependency setup, human-initiated pinned artifact acquisition, local verification, training and evaluation. It must fail clearly if required local assets are absent.

Treat retrieved text and tool proposals as untrusted data. Enforce access policy before retrieval, retain provenance and offsets, separate statistical computation from generated prose, and evaluate task utility independently of fluency. QLoRA-style CPU demonstrations must state exactly which quantization/storage/gradient behavior they implement and which GPU/NF4/memory properties they do not measure.

Use exact references from primary papers and versioned official documentation. Update the authoring specifications as well as generated lesson bundles. No em dashes.

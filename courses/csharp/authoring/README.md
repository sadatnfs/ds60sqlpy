# Reproducible C# authoring

Run `python courses/csharp/authoring/build.py` from the repository root. Only the Python standard library is needed for generation. `foundations.py`, `composition.py` and `advanced.py` contain the original chapter specifications, examples, task contracts and diagnosis. `render.py` writes the published artifacts and manifests.

The source order defines stable IDs csharp-001 through csharp-048. Do not reorder existing specifications or renumber them after publication. Additive work requires a reviewed stable-ID strategy. The three stages each have sixteen lessons.

To check reproducibility, hash the track, manifest, guides, learners and solutions, rerun build.py, and compare hashes. Generated HTML belongs to the shared reader generator and is never edited here. Project fixtures are directly authored source, not output of build.py.

Runtime checks are separate from generation. Every reference combines both worked scenarios with explicit invariant checks. Independent and transfer tasks can have several valid designs; explanatory solutions state the reasoning rather than promising a hidden grading engine. The profile `csharp-dotnet` must actually compile and execute source before runtime success is claimed.

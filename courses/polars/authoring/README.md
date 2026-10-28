# Polars authoring

Maintain original lesson prose and practice in units.json and complete executable
programs in ../references/. Each reference supplies example_one and example_two
with assertions and a deterministic completion marker. All programs are local
and bounded; the two benchmark cases report observations without timing promises.

Run `python courses/polars/authoring/build.py` from the repository root, then
`python courses/polars/authoring/build.py --check`. The publisher extracts complete
worked programs through their function dependencies, retains raw source and
generates guides, learner starting points, explanatory solutions and manifests.
Format references before publishing. Root owns shared HTML and TeX generation.

Independent tests check grain, fanout, temporal availability and null policies
as well as executing the references in the prepared data-engineering profile.
A host without Polars must record an explicit optional-runtime skip. Use the
actual Docker reference runner for delivery qualification.

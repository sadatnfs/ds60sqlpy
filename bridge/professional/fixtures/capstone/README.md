# Synthetic capstone evidence

All values are course-authored fictional fixtures. There is no personal,
workplace, production, or externally licensed dataset.

- `golden_product.json` independently declares one row per invoice A, B, and C.
  It is expected evidence, not generated output of the reference transformer.
- `incident_product.json` has the same count and total cents but changes B,
  omits the zero-valued C invoice, and introduces D. It demonstrates a failed
  data contract, not a real historical incident.
- `source_lines.json` supplies three uniquely identified line facts. A and B
  have lines; the separately declared complete parent manifest also includes C.

Money is nonnegative integer cents in one synthetic currency. Invoice identity
is exact case-sensitive text without outer whitespace. No duplicate source
winner policy is supplied, so repeated line IDs are rejected. Editing the
golden fixture to fit a failing transformation invalidates the exercise.

The module's default main only reads these files and prints local evidence.
Any evidence report is written only to a caller-provided unused path. Keep
learner output separate from this immutable fixture directory.

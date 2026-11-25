# R study guide

Every chapter guide in this track follows the same run routine, the same
six-exercise structure and the same comparison habit. This page explains those
shared rules once. Each chapter guide keeps what belongs to its own mechanism:
the starter's inputs and what to predict before running them, the worked
examples, the exercises and the specific assertions its reference makes.

Chapters r-001 to r-050 print values. Chapters r-051 to r-060 draw figures as
well, so read [Figures](#figures) before starting them.

## Run a chapter

Open the chapter in `/classroom` and choose the prepared `r-statistics`
profile. Each Run evaluates one `main.R` script in a fresh offline R process.
Nothing survives between runs: a variable you defined in an earlier Run is
gone, so every input a script needs must be defined in that script. When a
result looks wrong, first check that the script actually creates every object
it uses.

Each chapter has three files:

- the starter in `lessons/r-0NN.R`, which supplies the inputs and one TODO per
  exercise;
- the complete reference in `solutions/r-0NN_reference.R`, which ends by
  printing `r-0NN reference checks passed`;
- the explained answers in `solutions/r-0NN_solutions.md`, which give the
  reasoning behind each exercise.

Every worked example in a guide is a standalone script. Paste one into an
empty `main.R` and it runs on its own, with its own inputs and its own
`stopifnot()` checks.

Save your source and notes separately from saved run output; the output is a
record of one run, not your program. No chapter installs packages or
downloads data. If a script seems to need either, it has stepped outside the
chapter's contract.

## Figures

Base graphics calls such as `plot()` and `hist()` draw immediately and are
captured as PNG figures. A ggplot2 or Plotly object draws nothing until it is
printed, so in a script call `print(chart)` explicitly; an object that is only
assigned leaves no figure. Plotly figures use the prepared interactive browser
renderer.

The classroom keeps at most two figures per run. If a chapter asks for more,
split the work across runs or check the built data instead of the image.

A temporary file written inside a run, such as a PNG from `tempfile()`, is not
a download. It disappears with the run's process, so treat it as evidence that
the device wrote valid bytes, not as a saved figure.

## What a passing run proves

Each reference ends with `stopifnot()` assertions on small synthetic inputs.
When they all pass, those specific assertions held in the reported
environment. That is all a passing run proves. It does not prove correctness
for every input, statistical validity for a population the inputs were not
drawn from, or compatibility with package versions that were not tested. Each
explained answer names what its own checks cover and what they leave open.

## Compare with the reference

Compare your implementation with the reference only after keeping your own
attempt. Different readable implementations can satisfy the same behavioral
contract, so a different shape is not a mistake. Inspect type, shape,
missingness and boundary behavior alongside the printed numbers. When your
result differs, find the first input where the two programs disagree and
explain why before changing anything.

## Package versions

The prepared environment uses R 4.6.1, R6 2.6.1, S7 0.2.2, ggplot2 4.0.3 and
Plotly 4.12.1. The examples rely on that checked-in dependency contract.
Running them against other package versions needs a fresh compatibility check.

## Moving through chapters

Each guide lists its direct prerequisites at the top and the chapters that
build on it at the end. The [course map](README.md) shows the whole route.
Chapters r-041 to r-050 apply statistical models, so read the
[statistics tutorial](../statistics-ml/README.md) alongside them for the
assumptions the R code does not check.

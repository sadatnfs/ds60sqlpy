# R curriculum guidance

Read the root guidance and [authoring contract](authoring/README.md). The subject
uses `r-statistics`, one `main.R` script per fresh offline R process. Do not add
package installation, network reads, hidden session dependencies or host paths.

Durable units are `authoring/units/r-001.json` through `r-060.json`. The assembler
owns the track, admission, starter, guide and solution artifacts. Edit the JSON
first. Preserve IDs, direct prerequisites, code-fence parity and saved-pad identity.
Do not hand-edit generated HTML or change a reference without its explained cases.

Teach type, shape, missingness, units and record grain alongside syntax. Preserve
meaningful differences among S3, S4, R6 and S7 rather than presenting them as aliases.
A categorical factor code is not its numeric label. A duplicated join is not a
valid many-to-one lookup. A successful process exit is not statistical validity.

Base graphics are captured as PNG. Use explicit `print()` for ggplot2 and Plotly
objects in scripts. At most two figures are retained per run. File creation,
figure capture and actual browser display are different evidence. Do not claim
that an ordinary temporary run file is a permanent learner download.

Prepared versions are R 4.6.1, R6 2.6.1, S7 0.2.2, ggplot2 4.0.3 and Plotly 4.12.1.
Check the maintained dependency lock before changing package-specific claims.
Multi-file package development is a separate optional contributor workflow; the
classroom editor remains a single-script surface. No em dashes or slogans.

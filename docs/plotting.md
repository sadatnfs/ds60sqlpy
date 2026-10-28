# Charts, tables and reports in the classroom

The [data-visualization course](../courses/data-visualization/README.md) compares
Python and JavaScript implementations using the same data and analytical
questions. The [R course](../courses/r/README.md) covers base graphics, ggplot2 and
Plotly alongside statistical modeling.

| Workspace          | Display operation                                                | Saved evidence                                      |
| ------------------ | ---------------------------------------------------------------- | --------------------------------------------------- |
| Python Core        | `plt.show()` or Plotly `fig.show()`                              | PNG or interactive figure data attached to the run  |
| R statistics       | Base `plot(...)`, `print(ggplot_object)`, `print(plotly_object)` | PNG or interactive figure data attached to the run  |
| Julia | `DS60Plots.show_plotly(...)` from the prepared classroom helper | Bounded Plotly data attached to the run |
| Python structured data | `publish_table(...)` or `publish_report(...)` | A bounded table or JSON report attached to the run |
| Browser JavaScript | `Plotly.newPlot(...)` using the bundled `Plotly` global          | Browser observation with its exact submitted source |

Python display hooks load only when the program imports a plotting library.
Plain Python programs do not import those libraries. Notebook execution retains
its cell and inline-Matplotlib behavior. Other numerical worker profiles only
support plotting libraries actually installed in that profile.

## Python

```python
import plotly.graph_objects as go

fig = go.Figure(go.Scatter(x=[1, 2, 3], y=[2, 5, 4], mode="lines+markers"))
fig.update_layout(
    title="Observed response",
    xaxis_title="Visit",
    yaxis_title="Response",
    meta={
        "description": "Response rises at visit two, then falls at visit three.",
        "table": {"columns": ["Visit", "Response"], "rows": [[1, 2], [2, 5], [3, 4]]},
    },
)
fig.show()
```

The optional description and table are rendered as ordinary accessible text
beside the chart. Include units and an interpretation. A figure's appearance is
not evidence that its underlying aggregation or uncertainty calculation is valid.

## Structured tables and reports

Use the prepared Python helper when a small result table or diagnostic record
is more useful than a chart:

```python
from ds60sqlpy.plot_artifacts import publish_report, publish_table

publish_table(
    ["Split", "Rows", "Brier score"],
    [["validation", 40, 0.18]],
    description="Synthetic held-out validation; lower Brier score is better.",
)
publish_report(
    {"feature_contract": "v1", "training_rows": 77, "decision": "review"},
    description="The fitted model's local evidence record, not deployment approval.",
)
```

These two calls use the entire two-output budget for that Run. A table/report
and a chart share the same budget; there is no separate quota for each kind.
Reports are finite JSON data and tables contain scalar or missing values.
Descriptions explain grain, units, assumptions and limits. The helper writes
into the job's anchored output destination even if the program changes its
working directory. Publication uses atomic replacement so a failed append does
not overwrite a previously saved output file.

All outputs remain attached to the exact submitted source. Opening a saved
result displays it without recalculation. Table or JSON text is escaped and
never treated as trusted page HTML. Use strings for integer identifiers outside
JavaScript's exact range, from -9007199254740991 through 9007199254740991.
Unsafe integers reject rather than silently rounding; the same rule applies to
chart metadata and accessible data tables. Convert unsupported Decimal or date
objects explicitly so their intended representation is clear.

A direct Python `publish_*` call can raise a validation/storage error. Handle
that error explicitly if the report is optional and keep the numerical result
available. The fixed Stan/dbt adapters preserve their real computation status
and print capture warnings for optional publication failures. Do not hide an
actual model, compiler or database failure behind a reporting exception.

## Julia

The prepared worker defines `DS60Plots` before the learner script runs:

```julia
using .DS60Plots

show_plotly(
    [Dict("type" => "scatter", "x" => [1, 2], "y" => [3, 5])];
    layout=Dict(
        "title" => Dict("text" => "Measured response"),
        "meta" => Dict(
            "description" => "Two synthetic visits; this line is not a fitted trend.",
            "table" => Dict("columns" => ["Visit", "Response"], "rows" => [[1, 3], [2, 5]]),
        ),
    ),
    description="Synthetic response by visit",
)
```

`DS60Plots` is a classroom helper, not a standard Julia plotting package or a
claim that Plots.jl is installed. It writes bounded Plotly data; the server
validates it again before storage. Use the subject's documented helper path
when running Julia examples outside the worker. The [Julia guide](../courses/julia/README.md)
identifies prepared packages and optional external projects.

## R

```r
library(ggplot2)

values <- data.frame(visit = 1:3, response = c(2, 5, 4))
chart <- ggplot(values, aes(visit, response)) +
  geom_point() +
  labs(title = "Observed response", x = "Visit", y = "Response")
print(chart)
print(plotly::ggplotly(chart))
```

R scripts do not automatically print assigned plot objects. Use explicit `print`
for ggplot2 and Plotly. Base graphics draw into the prepared headless PNG device.
Files created in a job directory are temporary; the supported captured figures
are retained with the run. Multi-file reports, Shiny applications and separately
prepared projects use their own documented workflows.

## JavaScript and saved figures

The JavaScript preview provides `Plotly`, `d3`, `#chart` and captured console
output. Libraries are bundled locally. Network requests and external scripts
are blocked. Keep descriptions and semantic data tables in the page and test
controls with the keyboard. Live preview requires an explicit opt-in; manual
Run or Save observation creates a saved browser record.

Captured Plotly data from Python, R, Julia and fixed runtime adapters is rendered
in a separate opaque iframe. Hover, zoom,
legend and authored controls work within it. The chart toolbar can export an
image, and **Download figure JSON** exports the saved figure specification.
Opening run history renders its saved chart data without executing the source
or replacing the current draft.

The saved-chart viewer fits its available width and height when resized or
reopened. This changes only the rendering copy. **Download figure JSON** retains
the original saved data and layout, including any authored width and height.

## Limits and diagnostics

A worker run retains at most two outputs in total, across PNG, Plotly, table and
JSON kinds, with a combined serialized limit of 384,000 bytes. A Plotly
specification, table/report artifact or decoded PNG is limited to 180,000 bytes;
PNG pixel dimensions are also bounded. These limits apply to examples intended for
the classroom, not general plotting-library capabilities. Reduce point counts,
use meaningful aggregation and avoid embedding large datasets in hover text.

The bundled Cartesian Plotly distribution supports scatter, bar, box, histogram,
heatmap, contour, violin, pie and related Cartesian traces. WebGL, geographic
maps, external image sources and separately hosted applications need a prepared
external project. Animated frames must satisfy the same data and offline rules.
The accessible table supports up to 12 columns and 100 rows with finite scalar
values or missing values.

A figure-storage warning is separate from the program's execution result. Retain
printed numerical checks and captions even when plotting. Do not rerun an
expensive calculation solely to recover a chart without first checking its
saved receipt and source.

## Declared outputs for reference programs

A subject can maintain `figure-contracts.json` for reference outputs that are
part of the lesson's promised evidence. Supported kinds are `png`, `plotly`,
`table` and `json`; contracts specify counts and, where appropriate, required
descriptions and table rows. The complete module reference checker reads these
through `scripts/declared_outputs.py`. An exit-zero program with missing required
outputs fails that check. Keep numerical correctness tests independent of this
structural check and verify browser/history/persistence behavior separately.

Stan's fixed operation publishes an actual diagnostic summary table and a trace
from two short chains. Undefined diagnostics for constant quantities appear as
missing values; a short run is not proof of convergence. dbt's SQL-model operation
publishes its actual bounded relation and compilation/run metadata. Neither
adapter invents a result from source text.

## Reading figures saved by earlier versions

Earlier Plotly receipts can contain numeric integers outside the browser's exact
range. Saved-result reading validates the complete figure shape, size and offline
content rules, then creates a display-only view. A figure with these integers is
withheld from rendering with an explicit explanation; valid sibling figures keep
their original order and numbering. Source, printed output, execution status and
receipt identity remain accessible.

**Download original figure JSON** exports the original figure data as
server-preserved JSON text. The browser writes that text directly to the download,
so large numeric integer literals retain their exact values. Original receipt
files retain their exact bytes. Reading history does not rewrite those files,
rerun source or mark learning progress.

New output publishers, worker results and receipt writes retain strict integer
validation. Publish large identifiers as explicit strings. Malformed figures,
invalid receipt identities, unsafe paths and exceeded resource limits continue
to fail their normal checks; the compatibility path applies only to the earlier
Plotly integer representation.

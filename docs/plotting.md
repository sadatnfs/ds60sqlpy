# Plotting in the classroom

The [data-visualization course](../courses/data-visualization/README.md) compares
Python and JavaScript implementations using the same data and analytical
questions. The [R course](../courses/r/README.md) covers base graphics, ggplot2 and
Plotly alongside statistical modeling.

| Workspace          | Display operation                                                | Saved evidence                                      |
| ------------------ | ---------------------------------------------------------------- | --------------------------------------------------- |
| Python Core        | `plt.show()` or Plotly `fig.show()`                              | PNG or interactive figure data attached to the run  |
| R statistics       | Base `plot(...)`, `print(ggplot_object)`, `print(plotly_object)` | PNG or interactive figure data attached to the run  |
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

Python and R figure data is rendered in a separate opaque iframe. Hover, zoom,
legend and authored controls work within it. The chart toolbar can export an
image, and **Download figure JSON** exports the saved figure specification.
Opening run history renders its saved chart data without executing the source
or replacing the current draft.

The saved-chart viewer fits its available width and height when resized or
reopened. This changes only the rendering copy. **Download figure JSON** retains
the original saved data and layout, including any authored width and height.

## Limits and diagnostics

A worker run retains at most two figures, with a combined serialized limit of
384,000 bytes. A Plotly specification or PNG is limited to 180,000 bytes; PNG
pixel dimensions are also bounded. These limits apply to examples intended for
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

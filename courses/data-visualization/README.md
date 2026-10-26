# Scientific visualization with Plotly

Eight lessons teach the same scientific objectives through Python and
JavaScript browser variants. The canonical Python route uses the prepared
Python Core profile and captured `fig.show()` output. The JavaScript variant
uses the offline browser preview with bundled `window.Plotly`.

1. [Records, traces and honest encodings](guides/viz-001.md)
2. [Aggregation, missingness and distributions](guides/viz-002.md)
3. [Uncertainty and effect displays](guides/viz-003.md)
4. [Filters and linked inspection](guides/viz-004.md)
5. [Time series and forecast evidence](guides/viz-005.md)
6. [Paired model comparisons](guides/viz-006.md)
7. [Bounded rendering and reduction](guides/viz-007.md)
8. [Accessible output and figure export](guides/viz-008.md)

Choose the subject on `/classroom`, select a lesson and preserve your saved
draft when switching language variants. Read the worked cases before attempting
the six specified tasks. Complete executable references and explanatory
solutions are separate and can be revealed for comparison. A run marker records
an observation, not statistical validity or mastery.

Every reference supplies a caption and exact-value table. Python uses plain
metadata for the shared figure panel and prints readable values; browser
references create native tables and controls. All data is synthetic and inline.
No Plotly account, Dash server, CDN, model download, map tiles or external data
service is required. Default examples use bounded Cartesian SVG traces.

The statistics book remains tutorial-only and provides the underlying
[experiment](../statistics-ml/tutorials/experimentation/README.md),
[model evaluation](../statistics-ml/tutorials/learning/07-validation-as-a-procedure.md)
and [scientific case](../statistics-ml/tutorials/science/README.md) interpretations.
The existing [D3 specialization](../javascript-typescript/README.md) teaches
lower-level browser graphics; these Plotly lessons do not replace it.

## Authoring and qualification

Guides are directly authored. `authoring/python_cases.py`,
`authoring/browser_cases.js` and the task/solution metadata in `authoring/units.json`
are durable sources. Run `authoring/build.py` after editing them, then
format and validate generated references. `fixtures/plotly-inventory.json`
identifies all eight paired cases for numerical and real-browser qualification.
Source parsing, figure creation, browser interaction, offline delivery and
accessibility are distinct checks and should be reported separately.
